const express = require('express');
const router = express.Router();
const transactionController = require('../controllers/transactionController');
const authMiddleware = require('../middleware/authMiddleware');

/**
 * Notice how we put 'authMiddleware' before the controller? 
 * This means the request MUST pass the security check first.
 */

// Route to add a transaction
router.post('/', authMiddleware, transactionController.addTransaction);

// Route to get transactions (with search/filter/pagination)
router.get('/', authMiddleware, transactionController.getTransactions);

// Route to get dashboard summary
router.get('/summary', authMiddleware, transactionController.getSummary);

// Route to update a specific transaction
router.put('/:id', authMiddleware, transactionController.updateTransaction);

// Route to delete a specific transaction
router.delete('/:id', authMiddleware, transactionController.deleteTransaction);

module.exports = router;