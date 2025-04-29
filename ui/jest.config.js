module.exports = {
    testEnvironment: "jsdom",
    transform: {
      "^.+\\.jsx?$": "babel-jest"
    },
    moduleNameMapper: {
      "\\.(css|less|scss|sass)$": "identity-obj-proxy" // Ignore CSS imports
    },
    transformIgnorePatterns: [
      "/node_modules/(?!axios)" // Allow Jest to transform axios
    ],
};