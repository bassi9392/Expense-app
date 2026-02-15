const jwt = require('jsonwebtoken');

const authMiddleware = (req, res, next) => {
    // 1. Get the token from the request header (it usually looks like "Bearer <token>")
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    // 2. If there is no token, deny access
    if (!token) {
        return res.status(401).json({ message: "No token, authorization denied" });
    }

    try {
        // 3. Verify the token using our secret key from the .env file
        const decoded = jwt.verify(token, process.env.JWT_SECRET);

        // 4. Attach the user data to the "req" object
        // This is how transactionController knows that req.user.id exists!
        req.user = decoded;

        // 5. Move to the next step (the actual Controller)
        next();
    } catch (error) {
        res.status(401).json({ message: "Token is not valid" });
    }
};

module.exports = authMiddleware;