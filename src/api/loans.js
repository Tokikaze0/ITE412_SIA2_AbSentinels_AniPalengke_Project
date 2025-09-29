const express = require("express");
const router = express.Router();

let loans = [
  { id: 1, borrowerId: 1, amount: 5000, status: "active" }
];

// GET all loans
router.get("/", (req, res) => {
  res.json(loans);
});

// POST new loan
router.post("/", (req, res) => {
  const { borrowerId, amount, status } = req.body;
  const newLoan = { id: loans.length + 1, borrowerId, amount, status };
  loans.push(newLoan);
  res.json(newLoan);
});

module.exports = router;
