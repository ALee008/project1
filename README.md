# Project 1

Web Programming with Python and JavaScript

---

The project is structured as follows:

```
project_0
│   application.py
|   books.csv
|   goodreads_requests.py
|   import.py
|   project_tools.py
|   README.md
|   requirements.txt
|   resource.py
|   set_env.sh
|
└───templates
|   │   add_review.html
|   │   index.html
|   |   layout.html
|   |   layout_books.html
|   |   layout_credentials.html
|   |   login.html
|   |   message_for_user.html
|   |   my_reviews.html
|   |   nav_bar.html
|   |   register.html
|   |   search.html
|
└───static
│   │   books.jpg
│   │   login.css
|   |   navigation_bar.css
|   |   style.css
|   |   workaround.css
│
└───sqls
│   │   ddl_book_reviews.sql
```
---
Preparing the database
---
The `books.csv` file was uploaded to the database using `import.py`. The tables were created with the sql statements
in `ddl_book_reviews.sql`. 

The Flask Application
---
The main logic is implemented in `application.py`. Besides the standard imports to get the flask application running, 
`flask_bcrypt` is imported to hash the passwords in the database. The modules `project_tools` and `goodreads_requests` 
are added by me. So is the module `resource` in `goodreads_requests`.

#### `project_tools`
Is meant to contain functions to support the main application.

#### `goodreads_requests`
Contains the function to import data using the goodreads api. In a real project the api key should not be exposed. 
Therefore it is stored in an extra file, `resource.py` that would normally not be uploaded to github.

The html Templates
---
`layout.html` is the parent template that all pages import to incorporate the navigation bar, padding and margins. 
`login.html` and `register.html` inherit additional formatting from `layout_credentials.html`. `message_for_user.html` 
serves as a template for a page that informs users about different event like 'login successful', etc.  

Further html files
---
`index.html` is the starting page. It contains a background image and a text field.

Further Remarks
---
#### `sqlalchemy.exc.OperationalError`
Sometimes this error occurs during login. According to the sqlalchemy documentation this error is "related to the 
database’s operation and not necessarily under the control of the programmer", 
[see here](https://docs.sqlalchemy.org/en/13/errors.html#operationalerror).

#### html formatting problems
In `search.html` the book details page is referenced by an `href` link. My first attempt was using dynamic routing where
isbn is the parameter to find the book details. But for some reasons which I could not figure out the locally linked 
css file was not correctly imported in `layout_books.html`. I have posted the problem on 
[stackoverflow](https://stackoverflow.com/questions/61573835/flask-dynamic-routing-causes-render-template-to-ignore-jinjer2-html-formattin/61574077?noredirect=1#comment108939850_61574077) 
and [r/cs50](https://www.reddit.com/r/cs50/comments/gcxu0e/cs50s_web_programming_with_python_and_javascript/) 
unfortunately without success. I would appreciate your feedback on this matter if you have any idea that causes this
problem.
