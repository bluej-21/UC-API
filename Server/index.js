/**
 * Created by J on 5/14/2016.
 */
var express = require("express");
var app = express();

app.set("port", (process.env.PORT || 8000));
app.use(express.static(__dirname + '/public'));

app.get("/", function(req,res){
  res.send("Main Page");
});

app.use("/ucla", require("./routes/uclaRouter"));
app.use("/ucsd", require("./routes/ucsdRouter"));

app.listen(app.get("port"), function(){
  console.log("UC-API is running on port", app.get("port"));
});