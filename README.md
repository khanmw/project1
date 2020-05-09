README.md
Harvard CS50 Web and Python Programming Course Project name: Project 1

Description: I created a HTML site, “Monterey Books” that stores book information, including written reviews and ratings as well as 3rd party data pulls from Goodreads.com.

Authentication: Users are able to register, login and logout.

Import: I imported the books.csv file of 5000 books into PostgreSQL using the import.py file and created three tables: users, books and reviews.

Search: Once a user logs in, they can search for an ISBN, book or author using a single search box. Case doesn’t matter, as I’ve coded the search to be case insensitive. Fuzzy logic using LIKE operator allows one to search for partial key words/ISBN.

Book Page: When users click on a book, they’re taken to a book page, displaying details of the book, including Goodreads reviews which were pulled via Python’s “requests” module. This page also displays reviews found in my PostgreSQL database and allows entry of a 5-point rating and reviews. Multiple reviews result in overwriting previous version via the SQL UPDATE command. Once committed, the page refreshes with the review appearing on the same book page.

API: For direct “GET” requests via an integration, the “/api/<isbn>” capability allows programmatic access to book details in JSON format. Please note that for each book’s review counts and average scores requirements I assumed you asked for data from my database tables—not a repull from Goodreads. I pulled both book and review details using a single SQL query that employs a LEFT JOIN. If not ISBN is provided via the API, I return a custom 404 error.
