const { Sequelize } = require('sequelize');
const path = require('path');

/**
 * We are initializing Sequelize to work with SQLite.
 * 'dialect' tells Sequelize we are using SQLite.
 * 'storage' tells Sequelize WHERE to save the database file.
 */
const sequelize = new Sequelize({
  dialect: 'sqlite',
  // This creates a file named 'database.sqlite' in your root folder
  storage: path.join(__dirname, '../database.sqlite'), 
  logging: false, // Set to true if you want to see the SQL queries in your terminal
});

// We export this 'sequelize' instance so our Models (User, Transaction) can use it.
module.exports = sequelize;