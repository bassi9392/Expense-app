const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

// When someone POSTS to /api/auth/register, run the register function
router.post('/register', authController.register);

// When someone POSTS to /api/auth/login, run the login function
router.post('/login', authController.login);

module.exports = router;