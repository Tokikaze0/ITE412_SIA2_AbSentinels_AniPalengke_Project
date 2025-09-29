const express = require("express");
const router = express.Router();

let borrowers = [
  { id: 1, name: "Juan Dela Cruz", email: "juan@email.com" }
];

// GET all borrowers
router.get("/", (req, res) => {
  res.json(borrowers);
});

// POST new borrower
router.post("/", (req, res) => {
  const { name, email } = req.body;
  const newBorrower = { id: borrowers.length + 1, name, email };
  borrowers.push(newBorrower);
  res.json(newBorrower);
});

module.exports = router;
