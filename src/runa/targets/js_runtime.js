/**
 * Runa Runtime Library for JavaScript
 *
 * This file provides runtime support for Runa programs compiled to JavaScript.
 */

// Utility function for working with named arguments
function extractNamedArgs(args, defaults) {
    if (args.length === 1 && typeof args[0] === 'object' && args[0] !== null) {
        return { ...defaults, ...args[0] };
    }
    return defaults;
}

// String formatting for Runa
function formatString(str, ...args) {
    if (args.length === 1 && typeof args[0] === 'object' && args[0] !== null) {
        // Named formatting
        let result = str;
        for (const [key, value] of Object.entries(args[0])) {
            const placeholder = new RegExp(`\\{${key}\\}`, 'g');
            result = result.replace(placeholder, value);
        }
        return result;
    } else {
        // Positional formatting
        return str.replace(/\{\d+}/g, match => {
            const index = parseInt(match.slice(1, -1));
            return index < args.length ? args[index] : match;
        });
    }
}

// Add utility functions for lists
Array.prototype.add = function(item) {
    this.push(item);
    return this;
};

Array.prototype.remove = function(item) {
    const index = this.indexOf(item);
    if (index !== -1) {
        this.splice(index, 1);
    }
    return this;
};

// Length operation
function length(obj) {
    if (Array.isArray(obj)) {
        return obj.length;
    } else if (typeof obj === 'string') {
        return obj.length;
    } else if (obj && typeof obj === 'object') {
        return Object.keys(obj).length;
    }
    return 0;
}

// Runa pipeline operator
function pipeline(value, func) {
    return func(value);
}

// Runa partial application
function partial(func, ...args) {
    return function(...moreArgs) {
        return func(...args, ...moreArgs);
    };
}

// Runa function composition
function compose(...funcs) {
    return function(x) {
        return funcs.reduceRight((acc, func) => func(acc), x);
    };
}

// Runa map function
function map_function(func, collection) {
    return collection.map(func);
}

// Runa filter function
function filter_function(predicate, collection) {
    return collection.filter(predicate);
}

// Runa reduce function
function reduce_function(func, collection, initial) {
    if (initial !== undefined) {
        return collection.reduce(func, initial);
    }
    return collection.reduce(func);
}

// Pattern matching helpers
function is_type(value, type) {
    switch (type.toLowerCase()) {
        case 'integer':
            return Number.isInteger(value);
        case 'float':
            return typeof value === 'number' && !Number.isInteger(value);
        case 'string':
            return typeof value === 'string';
        case 'boolean':
            return typeof value === 'boolean';
        case 'list':
            return Array.isArray(value);
        case 'dictionary':
            return typeof value === 'object' && value !== null && !Array.isArray(value);
        default:
            return false;
    }
}

// Async utilities
async function gather(...promises) {
    return await Promise.all(promises);
}

async function sleep(seconds) {
    return new Promise(resolve => setTimeout(resolve, seconds * 1000));
}

// Export all utilities for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        extractNamedArgs,
        formatString,
        length,
        pipeline,
        partial,
        compose,
        map_function,
        filter_function,
        reduce_function,
        is_type,
        gather,
        sleep
    };
}