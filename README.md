# Star Jeans - A Data Engineer Project

This repository contains scripts about a web scraping of an e-commerce project. <br>

## Data Engineering Project for an E-Commerce

The objective of this project is:
- Perform web scraping of e-commerce
- Determine the raw materials needed to make the pants
- Determine the types of jeans pants and their colors
- Determine the best price to sell jeans pants

## Business Problem

Two businessmen, named Eduardo and Marcelo, wanted to start an e-commerce company called Star Jeans to sell men's jeans pants. The data scientist is responsible for determining the raw materials, types, colors, and best price to sell jeans pants. <br>

## Business Assumptions

* The data will be collected for two weeks at two different hours of the day
* The objective is to keep the company's initial operating costs low considering a small amount of jeans types
* Pocket material data were not considered
* "Product safety" attribute excluded for having 80 percent of NA values
* "More sustainable materials" attribute excluded for having 59 percent of NA values
* In the composition, when products with different percentages occur, was selected the material with the highest value
* The variables collected from website are:<br>

Variable | Definition
------------ | -------------
|product_id| Identification number of each product|
|fit| How the product fits on the body |
|product_name| The type of jeans pants |
|product_price| The price of jeans pants |
|color_name| The colors of jeans pants |
|style_id| The product code based on SKU (Stock Keeping Unit) |
|color_id| The id colors of jeans pants based on SKU (Stock Keeping Unit) |
|scrapy_datetime| The information from both date and time from when it was collected |
|size_number| Body heigt in centimeters |
|size_model| The first number is the waist circumference, and the second number is the inseam length, both in inches |
|cotton| Percent of cotton in the jeans pants |
|polyester| Percent of polyester in the jeans pants |
|spandex| Percent of spandex in the jeans pants |
|elasterell| Percent of elasterell in the jeans pants |

### Solution Strategy

The strategy to solve this challenge was:

Step 01 - Understanding the business model. <br>
Step 02 - Understanding the business problem. <br>
Step 03 - Collecting the datas by doing a webscrapping. <br>
Step 04 - Cleaning the data. <br>
Step 05 - Insert the data on a database. <br>
Step 06 - Execute the script automatically. <br>

### Conclusion

**This project is still in progress**


### Next Steps

**This project is still in progress**

----
**References:**
Course Python DS_ao_DEV from [Comunidade DS](https://www.comunidadedatascience.com/) 
