#!/usr/bin/env python3
"""
Runa Just-In-Time Compiler

This module implements a JIT compiler for the Runa language, which dynamically compiles
frequently executed code paths to native code for improved performance.
"""

import os
import sys
import time
import logging
import hashlib
import tempfile
import subprocess
from typing import Dict, List, Set, Tuple, Optional, Any, Callable, Union

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("runa.jit")

# Try to import optional dependencies
try:
    import llvmlite.binding as llvm
    LLVM_AVAILABLE = True
except ImportError:
    logger.warning("llvmlite not available. JIT compilation will use fallback methods.")
    LLVM_AVAILABLE = False

# Global JIT configuration
JIT_CONFIG = {
    "enabled": True,
    "threshold": 100,  # Number of executions before JIT compiling
    "optimization_level": 2,  # 0-3, higher is more aggressive
    "cache_dir": os.path.join(tempfile.gettempdir(), "runa_jit_cache"),
    "trace_execution": False,  # Enable to log execution counts and JIT compilations
    "warm_up_time": 2.0,  # Seconds of warm-up time before JIT kicks in
    "max_cache_size": 100 * 1024 * 1024,  # 100MB max cache size
    "min_function_size": 10,  # Minimum number of operations in a function to be JIT-compiled
}

# JIT execution statistics
JIT_STATS = {
    "compilation_count": 0,
    "execution_count": 0,
    "compilation_time": 0.0,
    "execution_time_saved": 0.0,
    "cache_hits": 0,
    "cache_misses": 0,
    "total_cache_size": 0,
}

# Function execution counters and JIT-compiled functions
execution_counters: Dict[str, int] = {}
compiled_functions: Dict[str, Callable] = {}
function_signatures: Dict[str, Dict] = {}
compilation_queue: List[str] = []
hot_functions: Set[str] = set()

# Initialize LLVM if available
if LLVM_AVAILABLE:
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    # Create an optimization pipeline
    pmb = llvm.create_pass_manager_builder()
    pmb.opt_level = JIT_CONFIG["optimization_level"]
    pmb.inlining_threshold = 100
    pm = llvm.create_module_pass_manager()
    pmb.populate(pm)

def configure_jit(config: Dict[str, Any]) -> None:
    """Configure the JIT compiler with the given settings."""
    global JIT_CONFIG
    for key, value in config.items():
        if key in JIT_CONFIG:
            JIT_CONFIG[key] = value
            logger.debug(f"JIT config updated: {key}={value}")
    
    # Create cache directory if it doesn't exist
    if not os.path.exists(JIT_CONFIG["cache_dir"]):
        os.makedirs(JIT_CONFIG["cache_dir"], exist_ok=True)

def get_jit_stats() -> Dict[str, Any]:
    """Get statistics on JIT compiler performance."""
    global JIT_STATS
    return {**JIT_STATS, "hot_functions": len(hot_functions)}

def clear_jit_cache() -> None:
    """Clear the JIT compilation cache."""
    global compiled_functions, execution_counters, hot_functions, JIT_STATS
    compiled_functions.clear()
    execution_counters.clear()
    hot_functions.clear()
    JIT_STATS["total_cache_size"] = 0
    JIT_STATS["cache_hits"] = 0
    JIT_STATS["cache_misses"] = 0
    
    # Remove cache files
    if os.path.exists(JIT_CONFIG["cache_dir"]):
        for file in os.listdir(JIT_CONFIG["cache_dir"]):
            try:
                os.remove(os.path.join(JIT_CONFIG["cache_dir"], file))
            except OSError:
                pass

def track_function_execution(func_id: str, ast_node: Any) -> None:
    """Track execution counts for a function to identify hot paths."""
    if not JIT_CONFIG["enabled"]:
        return
    
    global execution_counters, hot_functions, compilation_queue
    
    if func_id not in execution_counters:
        execution_counters[func_id] = 0
        function_signatures[func_id] = {
            "ast": ast_node,
            "first_seen": time.time(),
            "compiled": False
        }
    
    execution_counters[func_id] += 1
    count = execution_counters[func_id]
    
    # Check if we should compile this function
    if (count >= JIT_CONFIG["threshold"] and 
        func_id not in hot_functions and
        time.time() - function_signatures[func_id]["first_seen"] > JIT_CONFIG["warm_up_time"]):
        
        # Check if function is large enough to justify compilation
        if is_function_worth_compiling(func_id, ast_node):
            logger.debug(f"Function {func_id} queued for JIT compilation after {count} executions")
            hot_functions.add(func_id)
            compilation_queue.append(func_id)

def is_function_worth_compiling(func_id: str, ast_node: Any) -> bool:
    """Determine if a function is complex enough to benefit from JIT compilation."""
    # Simple operation count heuristic - can be expanded for better analysis
    op_count = count_operations(ast_node)
    return op_count >= JIT_CONFIG["min_function_size"]

def count_operations(ast_node: Any) -> int:
    """Count the number of operations in an AST node recursively."""
    if hasattr(ast_node, "children"):
        return 1 + sum(count_operations(child) for child in ast_node.children)
    elif isinstance(ast_node, (list, tuple)):
        return sum(count_operations(child) for child in ast_node)
    else:
        return 1

def process_compilation_queue() -> None:
    """Process pending JIT compilations in the background."""
    global compilation_queue, JIT_STATS
    
    if not compilation_queue:
        return
    
    # Take first item from the queue
    func_id = compilation_queue.pop(0)
    if func_id in compiled_functions:
        return
    
    # Compile the function
    ast_node = function_signatures[func_id]["ast"]
    start_time = time.time()
    
    try:
        compiled_func = compile_function(func_id, ast_node)
        if compiled_func:
            compiled_functions[func_id] = compiled_func
            function_signatures[func_id]["compiled"] = True
            compilation_time = time.time() - start_time
            JIT_STATS["compilation_count"] += 1
            JIT_STATS["compilation_time"] += compilation_time
            logger.info(f"JIT compiled function {func_id} in {compilation_time:.3f}s")
    except Exception as e:
        logger.warning(f"JIT compilation failed for {func_id}: {str(e)}")

def compile_function(func_id: str, ast_node: Any) -> Optional[Callable]:
    """Compile a function AST to native code using LLVM or fallback methods."""
    # Check cache first
    cache_key = compute_cache_key(func_id, ast_node)
    cached_func = load_from_cache(cache_key)
    if cached_func:
        JIT_STATS["cache_hits"] += 1
        return cached_func
    
    JIT_STATS["cache_misses"] += 1
    
    if LLVM_AVAILABLE:
        return compile_with_llvm(func_id, ast_node, cache_key)
    else:
        return compile_with_fallback(func_id, ast_node, cache_key)

def compute_cache_key(func_id: str, ast_node: Any) -> str:
    """Compute a cache key for a function AST."""
    # In a real implementation, we'd serialize the AST in a consistent way
    # For now, we use the function ID and a hash of the AST string representation
    ast_str = str(ast_node)
    return hashlib.sha256(f"{func_id}:{ast_str}".encode()).hexdigest()

def load_from_cache(cache_key: str) -> Optional[Callable]:
    """Load a compiled function from the cache."""
    cache_path = os.path.join(JIT_CONFIG["cache_dir"], f"{cache_key}.py")
    if os.path.exists(cache_path):
        try:
            # Load the module
            import importlib.util
            spec = importlib.util.spec_from_file_location(f"runa_jit_{cache_key}", cache_path)
            if spec is None or spec.loader is None:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.jit_function
        except Exception as e:
            logger.warning(f"Failed to load cached function {cache_key}: {str(e)}")
    return None

def compile_with_llvm(func_id: str, ast_node: Any, cache_key: str) -> Optional[Callable]:
    """Compile a function AST to native code using LLVM."""
    if not LLVM_AVAILABLE:
        return None
    
    try:
        # Convert AST to LLVM IR - this would be implemented in a real system
        # This is a placeholder for the actual AST to LLVM IR conversion
        llvm_ir = generate_llvm_ir_from_ast(ast_node)
        
        # Parse the IR
        module = llvm.parse_assembly(llvm_ir)
        
        # Optimize the module
        pm.run(module)
        
        # Create a JIT execution engine
        target_machine = llvm.Target.from_default_triple().create_target_machine()
        engine = llvm.create_mcjit_compiler(module, target_machine)
        
        # Finalize the object
        engine.finalize_object()
        
        # Get a pointer to the compiled function
        func_ptr = engine.get_function_address(func_id)
        
        # Wrap the function pointer - this would need more complex FFI in a real implementation
        # This is just a placeholder
        def jit_wrapper(*args):
            # In a real implementation, this would call the native function
            pass
        
        # Save to cache
        save_to_cache(cache_key, jit_wrapper)
        
        return jit_wrapper
    except Exception as e:
        logger.error(f"LLVM compilation error for {func_id}: {str(e)}")
        return None

def generate_llvm_ir_from_ast(ast_node: Any) -> str:
    """Generate LLVM IR from an AST node - placeholder implementation."""
    # This would be a complex part of a real JIT compiler
    # For now, return a simple placeholder module
    return """
    ; ModuleID = 'runa_jit'
    target triple = "x86_64-unknown-linux-gnu"
    
    define i32 @placeholder(i32 %arg) {
    entry:
      %result = add i32 %arg, 42
      ret i32 %result
    }
    """

def compile_with_fallback(func_id: str, ast_node: Any, cache_key: str) -> Optional[Callable]:
    """Compile a function using a fallback method like transpilation to Python."""
    try:
        # Convert AST to Python code
        python_code = generate_python_from_ast(ast_node, func_id)
        
        # Save to temporary file
        cache_path = os.path.join(JIT_CONFIG["cache_dir"], f"{cache_key}.py")
        with open(cache_path, "w") as f:
            f.write(python_code)
        
        # Update cache size tracking
        JIT_STATS["total_cache_size"] += os.path.getsize(cache_path)
        
        # Import the module
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"runa_jit_{cache_key}", cache_path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module.jit_function
    except Exception as e:
        logger.error(f"Fallback compilation error for {func_id}: {str(e)}")
        return None

def generate_python_from_ast(ast_node: Any, func_id: str) -> str:
    """Generate Python code from an AST node - placeholder implementation."""
    # This would be the Runa to Python transpiler in a real implementation
    # For now, return a placeholder function
    return f"""# Generated by Runa JIT compiler
# Function ID: {func_id}

def jit_function(*args, **kwargs):
    # This is a placeholder for actual compiled code
    # In a real implementation, this would contain the transpiled function
    return args[0] * 2 if args else 42
"""

def save_to_cache(cache_key: str, func: Callable) -> None:
    """Save a compiled function to the cache."""
    cache_path = os.path.join(JIT_CONFIG["cache_dir"], f"{cache_key}.py")
    
    # Check cache size limits
    if JIT_STATS["total_cache_size"] > JIT_CONFIG["max_cache_size"]:
        # Simple cache eviction: remove oldest files
        clean_oldest_cache_entries()
    
    # Generate a Python module that wraps the function
    with open(cache_path, "w") as f:
        f.write(f"""# Generated by Runa JIT compiler
# Cache key: {cache_key}
# Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}

# JIT wrapper function
jit_function = {func.__name__}
""")
    
    # Update cache size tracking
    JIT_STATS["total_cache_size"] += os.path.getsize(cache_path)

def clean_oldest_cache_entries() -> None:
    """Clean the oldest cache entries to make room for new ones."""
    if not os.path.exists(JIT_CONFIG["cache_dir"]):
        return
    
    # Get all cache files with their timestamps
    cache_files = []
    for file in os.listdir(JIT_CONFIG["cache_dir"]):
        file_path = os.path.join(JIT_CONFIG["cache_dir"], file)
        if os.path.isfile(file_path) and file.endswith(".py"):
            cache_files.append((file_path, os.path.getmtime(file_path)))
    
    # Sort by modification time (oldest first)
    cache_files.sort(key=lambda x: x[1])
    
    # Remove oldest files until we're under the limit
    current_size = JIT_STATS["total_cache_size"]
    target_size = JIT_CONFIG["max_cache_size"] * 0.8  # Aim for 80% of max
    
    for file_path, _ in cache_files:
        if current_size <= target_size:
            break
        
        try:
            file_size = os.path.getsize(file_path)
            os.remove(file_path)
            current_size -= file_size
            JIT_STATS["total_cache_size"] -= file_size
            logger.debug(f"Removed cache file: {file_path}")
        except OSError:
            pass

def execute_function(func_id: str, args: Tuple, kwargs: Dict) -> Any:
    """Execute a function, using the JIT-compiled version if available."""
    global JIT_STATS
    
    # Check if JIT is enabled
    if not JIT_CONFIG["enabled"]:
        return None  # Signal to use the interpreter
    
    # Check if we have a compiled version
    if func_id in compiled_functions:
        JIT_STATS["execution_count"] += 1
        compiled_func = compiled_functions[func_id]
        
        # Track execution time if configured
        if JIT_CONFIG["trace_execution"]:
            start_time = time.time()
            result = compiled_func(*args, **kwargs)
            execution_time = time.time() - start_time
            JIT_STATS["execution_time_saved"] += execution_time  # Estimate
            return result
        else:
            return compiled_func(*args, **kwargs)
    
    # Process the compilation queue if we have items pending
    if compilation_queue:
        process_compilation_queue()
    
    # Signal that we don't have a compiled version
    return None

def initialize() -> None:
    """Initialize the JIT compiler system."""
    # Create cache directory if it doesn't exist
    if not os.path.exists(JIT_CONFIG["cache_dir"]):
        os.makedirs(JIT_CONFIG["cache_dir"], exist_ok=True)
    
    logger.info(f"Runa JIT compiler initialized with threshold={JIT_CONFIG['threshold']}")

# Initialize the JIT system when the module is imported
initialize()

# Public API
__all__ = [
    "configure_jit",
    "get_jit_stats",
    "clear_jit_cache",
    "track_function_execution",
    "execute_function",
    "process_compilation_queue",
] 