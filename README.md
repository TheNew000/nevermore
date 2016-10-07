# Nevermore Twitter "Clone"

## Live Demo
[I'm an inline-style link](www.dannyarango.com/nevermore)

## Overview
Users can register profiles, view other user's profiles as well as post edit and delete the posts that they created.   Users may also interact with the posts by upvoting, downvoting, or favoriting the different posts.  There is a User Portal where Users can update their information as well as see a few stats. (Upvotes, Downvotes, "Faves")

What I enjoyed most about this project were all the various queries I devised to the gather information depending on the requests.  I loved the logic that goes into combining tables, not to mention the various Sum(), and Count() methods that allow us to learn even more about the data we're studying.  My greatest feat on this project was easily the query I wrote to gather all of the posts for a specific user, and show the data based off of user interactions for how many up/downvotes and favorites each one received:

```Python
SELECT JK.ID, 
JK.QUOTE, 
SUM(JK.UP) AS UP, 
SUM(JK.DOWN) AS DOWN, 
JK.Fave_Count FROM (SELECT poetry3.quote as QUOTE, 
poetry3.id as ID, 
poetry3.user_name as NAME, 
COUNT(CASE WHEN vote='DOWN' then `vote` end) AS DOWN,
COUNT(CASE WHEN vote='UP' then `vote` end ) AS UP,
COUNT(CASE WHEN fave='FAVE' then `fave` END) AS Fave_Count
FROM who_voted 
INNER JOIN poetry3 ON who_voted.comment_id = poetry3.id 
GROUP BY QUOTE, NAME, ID) AS JK 
WHERE JK.NAME = %s  # This would be a string in which the username is passed into
GROUP BY JK.QUOTE, JK.NAME, JK.ID 
ORDER BY UP DESC
```

In this query, I am retrieving each quote ID, the actual quote content itself, how many upvotes and downvotes each comment has received, and finally, how many times it's been given a "favorite."  But first, I need to create the subquery on this line: `...JK.Fave_Count FROM (SELECT poetry3.quote as QUOTE...` in which I count the various cases for each quote based on the user's name.  Even though I collect the user's name in the subquery I simply use it for grouping those posts that user made.  And then I ordered the list so the information would be displayed with the post that received the most upvotes first: `ORDER BY UP DESC`






## Technologies
- HTML
- CSS
- Bootstrap
- JavaScript
- AJAX
- Compass/SCSS
- Python
- Flask
- Jinja
- MySQL

## Requirements
`pip install flask`

`pip install flask-mysql`

`pip install bcrypt`

