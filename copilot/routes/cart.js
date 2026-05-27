const express = require('express');
const router = express.Router();

// Sample cart data (in a real app, this would be stored in a database)
// Structure: { userId: [{ productId, quantity, addedAt, product }] }
let userCarts = {};

// Sample product data reference (in real app, you'd import this or query from database)
const getProductById = (id) => {
    const products = [
        {
            id: 1,
            name: 'Wireless Headphones',
            description: 'High-quality wireless headphones with noise cancellation',
            price: 199.99,
            category: 'Electronics',
            inStock: true,
            imageUrl: 'https://example.com/headphones.jpg'
        },
        {
            id: 2,
            name: 'Smart Watch',
            description: 'Fitness tracking smart watch with heart rate monitor',
            price: 299.99,
            category: 'Electronics',
            inStock: true,
            imageUrl: 'https://example.com/smartwatch.jpg'
        },
        {
            id: 3,
            name: 'Coffee Mug',
            description: 'Ceramic coffee mug with thermal insulation',
            price: 24.99,
            category: 'Kitchen',
            inStock: true,
            imageUrl: 'https://example.com/mug.jpg'
        },
        {
            id: 4,
            name: 'Laptop Backpack',
            description: 'Durable laptop backpack with multiple compartments',
            price: 79.99,
            category: 'Accessories',
            inStock: false,
            imageUrl: 'https://example.com/backpack.jpg'
        },
        {
            id: 5,
            name: 'Bluetooth Speaker',
            description: 'Portable Bluetooth speaker with excellent sound quality',
            price: 89.99,
            category: 'Electronics',
            inStock: true,
            imageUrl: 'https://example.com/speaker.jpg'
        }
    ];
    
    return products.find(p => p.id === id);
};

// POST /api/cart - Add product to user's cart
router.post('/', (req, res) => {
    const { userId, productId, quantity = 1 } = req.body;
    
    // Validation
    if (!userId || !productId) {
        return res.status(400).json({
            success: false,
            message: 'User ID and Product ID are required'
        });
    }
    
    if (quantity <= 0) {
        return res.status(400).json({
            success: false,
            message: 'Quantity must be greater than 0'
        });
    }
    
    // Check if product exists
    const product = getProductById(parseInt(productId));
    if (!product) {
        return res.status(404).json({
            success: false,
            message: 'Product not found'
        });
    }
    
    // Check if product is in stock
    if (!product.inStock) {
        return res.status(400).json({
            success: false,
            message: 'Product is out of stock'
        });
    }
    
    // Initialize user cart if it doesn't exist
    if (!userCarts[userId]) {
        userCarts[userId] = [];
    }
    
    // Check if product already exists in cart
    const existingItemIndex = userCarts[userId].findIndex(item => item.productId === parseInt(productId));
    
    if (existingItemIndex > -1) {
        // Update quantity if product already in cart
        userCarts[userId][existingItemIndex].quantity += parseInt(quantity);
        userCarts[userId][existingItemIndex].updatedAt = new Date().toISOString();
    } else {
        // Add new item to cart
        const cartItem = {
            productId: parseInt(productId),
            quantity: parseInt(quantity),
            addedAt: new Date().toISOString(),
            product: product
        };
        userCarts[userId].push(cartItem);
    }
    
    res.status(201).json({
        success: true,
        message: 'Product added to cart successfully',
        data: {
            userId: userId,
            cartItems: userCarts[userId].length,
            totalItems: userCarts[userId].reduce((total, item) => total + item.quantity, 0)
        }
    });
});

// GET /api/cart/:userId - Get user's cart products
router.get('/:userId', (req, res) => {
    const { userId } = req.params;
    
    if (!userId) {
        return res.status(400).json({
            success: false,
            message: 'User ID is required'
        });
    }
    
    // Get user's cart or empty array if doesn't exist
    const userCart = userCarts[userId] || [];
    
    // Calculate cart summary
    const totalItems = userCart.reduce((total, item) => total + item.quantity, 0);
    const totalPrice = userCart.reduce((total, item) => total + (item.product.price * item.quantity), 0);
    
    res.json({
        success: true,
        data: {
            userId: userId,
            items: userCart,
            summary: {
                totalItems: totalItems,
                totalPrice: parseFloat(totalPrice.toFixed(2)),
                itemCount: userCart.length
            }
        },
        message: 'Cart retrieved successfully'
    });
});

// PUT /api/cart - Update product quantity in cart
router.put('/', (req, res) => {
    const { userId, productId, quantity } = req.body;
    
    if (!userId || !productId || quantity === undefined) {
        return res.status(400).json({
            success: false,
            message: 'User ID, Product ID, and quantity are required'
        });
    }
    
    if (!userCarts[userId]) {
        return res.status(404).json({
            success: false,
            message: 'Cart not found for user'
        });
    }
    
    const itemIndex = userCarts[userId].findIndex(item => item.productId === parseInt(productId));
    
    if (itemIndex === -1) {
        return res.status(404).json({
            success: false,
            message: 'Product not found in cart'
        });
    }
    
    if (parseInt(quantity) <= 0) {
        // Remove item if quantity is 0 or negative
        userCarts[userId].splice(itemIndex, 1);
        return res.json({
            success: true,
            message: 'Product removed from cart'
        });
    } else {
        // Update quantity
        userCarts[userId][itemIndex].quantity = parseInt(quantity);
        userCarts[userId][itemIndex].updatedAt = new Date().toISOString();
        
        return res.json({
            success: true,
            message: 'Cart updated successfully',
            data: userCarts[userId][itemIndex]
        });
    }
});

// DELETE /api/cart/:userId/:productId - Remove specific product from cart
router.delete('/:userId/:productId', (req, res) => {
    const { userId, productId } = req.params;
    
    if (!userCarts[userId]) {
        return res.status(404).json({
            success: false,
            message: 'Cart not found for user'
        });
    }
    
    const itemIndex = userCarts[userId].findIndex(item => item.productId === parseInt(productId));
    
    if (itemIndex === -1) {
        return res.status(404).json({
            success: false,
            message: 'Product not found in cart'
        });
    }
    
    const removedItem = userCarts[userId].splice(itemIndex, 1)[0];
    
    res.json({
        success: true,
        message: 'Product removed from cart successfully',
        data: removedItem
    });
});

// DELETE /api/cart/:userId - Clear entire cart for user
router.delete('/:userId', (req, res) => {
    const { userId } = req.params;
    
    if (!userCarts[userId]) {
        return res.status(404).json({
            success: false,
            message: 'Cart not found for user'
        });
    }
    
    const itemCount = userCarts[userId].length;
    userCarts[userId] = [];
    
    res.json({
        success: true,
        message: `Cart cleared successfully. Removed ${itemCount} items.`
    });
});

module.exports = router;