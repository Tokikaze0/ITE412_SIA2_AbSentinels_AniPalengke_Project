const express = require("express");
const app = express();
app.use(express.json());

// Import routes
const borrowerRoutes = require("./borrowers");
const loanRoutes = require("./loans");

app.use("/borrowers", borrowerRoutes);
app.use("/loans", loanRoutes);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`API running at http://localhost:${PORT}`);
});
