/**
 * Created by J on 5/14/2016.
 */
var express = require("express");
var router = express.Router();
var fs = require("fs");
var path = require("path");

router.get("/", function(req,res){
  res.send("UCSD Home Page");
});

router.get("/courses", function(req, res) {
  fs.readFile(path.join((__dirname, "../..", "Data/ucsd_courses.json")), function(err, data) {
    if(err) {
      res.send("error");
    }
    res.send(data);
  });
});

module.exports = router;