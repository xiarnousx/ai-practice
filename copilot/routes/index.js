const express = require('express');
const router = express.Router();

// Import route modules
const usersRouter = require('./users');
const productsRouter = require('./products');
const cartRouter = require('./cart');

// API routes
router.use('/users', usersRouter);
router.use('/products', productsRouter);
router.use('/cart', cartRouter);

// API info endpoint
router.get('/', (req, res) => {
    res.json({
        message: 'API is running',
        version: '1.0.0',
        endpoints: {
            users: '/api/users',
            products: '/api/products',
            cart: '/api/cart',
            health: '/health'
        }
    });
});

module.exports = router;