const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Ensure src directory is included in the resolver
config.resolver.platforms = ['ios', 'android', 'native', 'web'];

module.exports = config;
