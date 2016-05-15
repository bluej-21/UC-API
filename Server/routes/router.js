var express = require("express");
var router = express.Router();
var fs = require("fs");
var path = require("path");

router.get("/", function(req,res) {
  res.send("Home Page");
});

router.get("/ucla/courses", function(req, res) {
  fs.readFile(path.join((__dirname, "../..", "Data/ucla_courses.json")), function(err, data) {
    if(err) {
      res.send("error");
    }
    res.send(data);
  });
});

router.get("/ucsd/courses", function(req, res) {
  res.send("Haven't received UCSD yet");
});

module.exports = router;