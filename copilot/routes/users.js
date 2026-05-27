const express = require('express');
const router = express.Router();

// Sample data (in a real app, this would be a database)
let users = [
    { id: 1, name: 'John Doe', email: 'john@example.com' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
];

// GET /api/users - Get all users
router.get('/', (req, res) => {
    res.json({
        success: true,
        data: users,
        count: users.length
    });
});

// GET /api/users/:id - Get user by ID
router.get('/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const user = users.find(u => u.id === id);
    
    if (!user) {
        return res.status(404).json({
            success: false,
            message: 'User not found'
        });
    }
    
    res.json({
        success: true,
        data: user
    });
});

// POST /api/users - Create new user
router.post('/', (req, res) => {
    const { name, email } = req.body;
    
    if (!name || !email) {
        return res.status(400).json({
            success: false,
            message: 'Name and email are required'
        });
    }
    
    const newUser = {
        id: users.length + 1,
        name,
        email
    };
    
    users.push(newUser);
    
    res.status(201).json({
        success: true,
        data: newUser,
        message: 'User created successfully'
    });
});

// PUT /api/users/:id - Update user
router.put('/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const { name, email } = req.body;
    const userIndex = users.findIndex(u => u.id === id);
    
    if (userIndex === -1) {
        return res.status(404).json({
            success: false,
            message: 'User not found'
        });
    }
    
    if (name) users[userIndex].name = name;
    if (email) users[userIndex].email = email;
    
    res.json({
        success: true,
        data: users[userIndex],
        message: 'User updated successfully'
    });
});

// DELETE /api/users/:id - Delete user
router.delete('/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const userIndex = users.findIndex(u => u.id === id);
    
    if (userIndex === -1) {
        return res.status(404).json({
            success: false,
            message: 'User not found'
        });
    }
    
    const deletedUser = users.splice(userIndex, 1)[0];
    
    res.json({
        success: true,
        data: deletedUser,
        message: 'User deleted successfully'
    });
});

module.exports = router;