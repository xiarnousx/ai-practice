const express = require('express');
const router = express.Router();

// Sample product data (in a real app, this would be from a database)
let products = [
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

// GET /api/products - Get all products
router.get('/', (req, res) => {
    const { category, inStock } = req.query;
    
    let filteredProducts = products;
    
    // Filter by category if provided
    if (category) {
        filteredProducts = filteredProducts.filter(product => 
            product.category.toLowerCase() === category.toLowerCase()
        );
    }
    
    // Filter by stock status if provided
    if (inStock !== undefined) {
        const stockFilter = inStock === 'true';
        filteredProducts = filteredProducts.filter(product => product.inStock === stockFilter);
    }
    
    res.json({
        success: true,
        data: filteredProducts,
        count: filteredProducts.length,
        message: 'Products retrieved successfully'
    });
});

// GET /api/products/:id - Get product by ID
router.get('/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const product = products.find(p => p.id === id);
    
    if (!product) {
        return res.status(404).json({
            success: false,
            message: 'Product not found'
        });
    }
    
    res.json({
        success: true,
        data: product
    });
});

module.exports = router;