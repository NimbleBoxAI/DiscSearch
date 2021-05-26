# DiscSearch

Searching through the discrete image spaces. Can we search through 1k images &lt;5 seconds.

## Dataset

We started with writing custom scripts for scraping from `unsplash.com` but the files are too large for our usecase. 

### Unsplash Scraping

Go to any query eg [`unsplash.com/s/photos/iphone`](https://unsplash.com/s/photos/iphone) and scroll till you think you have sufficient images. Then open up console from inspect and type in the following instructions ([link](https://towardsdatascience.com/quickly-extract-all-links-from-a-web-page-using-javascript-and-the-browser-console-49bb6f48127b)):
```
var x = document.querySelectorAll("a");
var myarray = []
for (var i=0; i<x.length; i++){
var nametext = x[i].textContent;
var cleantext = nametext.replace(/\s+/g, ' ').trim();
var cleanlink = x[i].href;
myarray.push([cleantext,cleanlink]);
};
function make_table() {
    var table = '<table><thead><th>Name</th><th>Links</th></thead><tbody>';
   for (var i=0; i<myarray.length; i++) {
            table += '<tr><td>'+ myarray[i][0] + '</td><td>'+myarray[i][1]+'</td></tr>';
    };
 
    var w = window.open("");
w.document.write(table); 
}
make_table()
```

This will open up a new page, simply copy paste all the items in a single file. Now check out `notebooks/scrape.py` for how to get the correct image links.

### Others

- [link](http://chaladze.com/l5/) Linnaeus 5 dataset

## Files

- `dalle.py`: simple wrapper for using dall-e VAE from OpenAI.
- `notebooks/scrape.py`: code for getting images from unsplash.com
