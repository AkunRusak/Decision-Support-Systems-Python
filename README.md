# 📊 Multi-Criteria Decision Making (MCDM) Methods

Welcome to this repository! This project presents a curated overview of **18 popular Multi-Criteria Decision Making (MCDM)** methods, widely used in decision analysis, optimization, and ranking problems. These techniques are applied in various domains including engineering, business, healthcare, and information systems.

---

## 🔍 MCDM Techniques Explained

Each method brings a unique perspective to solving complex decision-making problems. Below is a brief overview of each method:

---

### A. Analytical Hierarchy Process (AHP)
AHP decomposes a decision problem into a hierarchy of more easily comprehended sub-problems. Pairwise comparisons are then made, and priorities are calculated using eigenvectors.

---

### B. Simple Additive Weighting (SAW)
SAW, also known as the weighted sum method, ranks alternatives by summing the products of criterion scores and their respective weights. It is intuitive and widely used for straightforward ranking.

---

### C. Profile Matching
This method assesses alternatives by comparing their profiles (attributes) to an ideal profile. It's often used in HR, student admissions, and recruitment systems.

---

### D. Entropy
Entropy method calculates objective weights for criteria based on the degree of diversity (or disorder) in the data. Less variation implies more important criteria.

---

### E. Weighted Product (WP)
The WP method multiplies criteria values raised to the power of their respective weights. It is a multiplicative alternative to SAW, effective when criteria are non-compensatory.

---

### F. TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)
TOPSIS identifies the solution closest to the ideal and farthest from the nadir solution. It’s suitable when trade-offs between criteria are involved.

---

### G. MOORA (Multi-Objective Optimization by Ratio Analysis)
MOORA optimizes multiple objectives simultaneously by normalizing and comparing them through ratio analysis.

---

### H. ELECTRE (Elimination and Choice Expressing Reality)
ELECTRE uses outranking relationships to eliminate less preferable alternatives. It’s designed for decision problems involving complex or conflicting preferences.

---

### I. ORESTE (Organization, Rangement Et Synthese De Donnes Relationnelles)
ORESTE avoids numerical weighting by using ordinal ranking and distance functions, making it suitable for qualitative evaluations.

---

### J. SMART (Specific, Measurable, Achievable, Relevant, and Time-Bound)
While originally a goal-setting framework, SMART in decision-making is used for assigning weights to criteria based on specific measurable attributes.

---

### K. VIKOR (VIšekriterijumsko KOmpromisno Rangiranje)
VIKOR focuses on ranking and selecting from a set of alternatives with conflicting criteria, emphasizing compromise solutions.

---

### L. ARAS (Additive Ratio Assessment)
ARAS evaluates alternatives based on their utility function values in a normalized decision matrix, integrating both additive and comparative concepts.

---

### M. MAUT (Multi-Attribute Utility Theory)
MAUT transforms subjective preferences into a utility function, facilitating rational decision-making under uncertainty and risk.

---

### N. COPRAS (Complex Proportional Assessment)
COPRAS considers both beneficial and non-beneficial criteria to compute the relative significance of alternatives in a proportional manner.

---

### O. MABAC (Multi-Attributive Border Approximation Area Comparison)
MABAC introduces a border approximation area to compare alternatives by their distances to an ideal solution in geometric space.

---

### P. MOOSRA (Multi-Objective Optimization System for Ranking Alternatives)
MOOSRA combines normalized weights and scores to optimize rankings under multiple objectives and constraints.

---

### Q. WASPAS (Weighted Aggregated Sum Product Assessment)
WASPAS hybridizes SAW and WP methods to provide more accurate and stable decision outcomes.

---

### R. PSI (Preference Selection Index)
PSI method ranks alternatives based on performance scores, calculated using normalized values, mean, and standard deviation—without requiring subjective weight assignment.

---

### S. DAS (Distance from Average Solution)
DAS ranks alternatives by measuring their deviation from the average solution. It’s a newer approach focused on identifying the most balanced option.

---

## 🧩 Why So Many Methods?

Each method has its strengths and is suited to different types of decision problems. Factors such as data type (quantitative vs qualitative), subjectivity, uncertainty, and the number of criteria or alternatives all influence which method is most appropriate.

---

## 💻 How to Use This Repository

- 📁 `/methods/` — Code implementation of each method in Python
- 📊 `/examples/` — Sample datasets with analysis
- 📚 `/docs/` — Mathematical formulations and reference papers

---

## 📚 References

- Saaty, T. L. (1980). *The Analytic Hierarchy Process*.
- Zavadskas, E. K., & Turskis, Z. (2011). *Multiple criteria decision making (MCDM) methods in economics: An overview*.
- Other scholarly articles and official publications per method.

---

## 🤝 Contributing

Want to contribute implementations or improvements? Feel free to submit a pull request or open an issue!

---

## 📌 License

This project is licensed under the [MIT License](LICENSE).

---

