const Transaction = require('../models/Transaction');
const { Op } = require('sequelize'); // Op stands for Operators (used for searching)

// 1. ADD a new transaction
exports.addTransaction = async (req, res) => {
    try {
        const { title, amount, category, date, notes } = req.body;
        // req.user.id comes from the Auth Middleware (which we will build next)
        const transaction = await Transaction.create({
            title,
            amount,
            category,
            date,
            notes,
            userId: req.user.id 
        });
        res.status(201).json(transaction);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// 2. GET all transactions (The Explorer Logic)
exports.getTransactions = async (req, res) => {
    try {
        // Get search/filter/pagination parameters from the URL
        // Example: /api/transactions?page=1&search=coffee&category=Food
        const { page = 0, limit = 10, search = '', category, startDate, endDate } = req.query;

        // Build the "Where" clause (Filtering logic)
        let whereClause = { userId: req.user.id };

        // If user is searching text
        if (search) {
            whereClause.title = { [Op.like]: `%${search}%` };
        }

        // If user filters by category
        if (category) {
            whereClause.category = category;
        }

        // If user filters by date range
        if (startDate && endDate) {
            whereClause.date = { [Op.between]: [startDate, endDate] };
        }

        // Fetch data from SQLite with Pagination
        const transactions = await Transaction.findAndCountAll({
            where: whereClause,
            limit: parseInt(limit),
            offset: parseInt(page) * parseInt(limit),
            order: [['date', 'DESC']] // Show newest first
        });

        res.json({
            totalItems: transactions.count,
            totalPages: Math.ceil(transactions.count / limit),
            currentPage: parseInt(page),
            data: transactions.rows
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// 3. UPDATE a transaction
exports.updateTransaction = async (req, res) => {
    try {
        const { id } = req.params;
        const transaction = await Transaction.findOne({ where: { id, userId: req.user.id } });
        
        if (!transaction) return res.status(404).json({ message: "Transaction not found" });

        await transaction.update(req.body);
        res.json({ message: "Updated successfully", transaction });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// 4. DELETE a transaction
exports.deleteTransaction = async (req, res) => {
    try {
        const { id } = req.params;
        const deleted = await Transaction.destroy({ where: { id, userId: req.user.id } });

        if (!deleted) return res.status(404).json({ message: "Transaction not found" });
        res.json({ message: "Transaction deleted" });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// 5. GET Dashboard Summary
exports.getSummary = async (req, res) => {
    try {
        const transactions = await Transaction.findAll({ where: { userId: req.user.id } });
        
        const totalExpenses = transactions.reduce((sum, item) => sum + item.amount, 0);
        
        // Group by category for the chart
        const categoryData = transactions.reduce((acc, item) => {
            acc[item.category] = (acc[item.category] || 0) + item.amount;
            return acc;
        }, {});

        res.json({
            totalExpenses,
            categoryData,
            recentTransactions: transactions.slice(0, 5) // Last 5 items
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};