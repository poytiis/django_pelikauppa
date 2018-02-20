var canvas = document.getElementById("myCanvas");
var ctx = canvas.getContext("2d");
canvas.style.background = "#D6D6D6";

var ballRadius = 10;
var x;
var y;
var dx;
var dy;
var squareHeight = 50;
var squareWidth = 50;
var squareX = (canvas.width-squareWidth)/2;
var squareY = (canvas.height-squareHeight)/2;
var upPressed = false;
var downPressed = false;
var rightPressed = false;
var leftPressed = false;
var speedFactor = 1;
var speedIncrease = 1.2;
var squareSpeed = 6;
var frameNumber = 0;
var scoreNumber = 0;
var levelCounter = 0;
var balls = [];

var animationFrame;

var gameOver = false;
var newGame = false;

$(document).ready( function() {
    "use strict";

    // Simulates "game over" when a score would be sent
    $("#submit_score").click( function ()
    {
        var msg =
        {
            "messageType": "SCORE",
            "score": parseFloat($("#score").text())
        };
        window.parent.postMessage(msg, "*");
    });

    // Sends this game's state to the service.
    // The format of the game state is decided
    // by the game
    $("#save").click( function ()
    {
        var msg =
        {
            "messageType": "SAVE",
            "gameState":
            {
                "score": parseFloat($("#score").text()),
                "speedFactor": parseFloat(speedFactor)
            }
        };
        window.parent.postMessage(msg, "*");
    });

    // Sends a request to the service for a
    // state to be sent, if there is one.
    $("#load").click( function ()
    {
        var msg =
        {
            "messageType": "LOAD_REQUEST",
        };
        window.parent.postMessage(msg, "*");
    });

    // Listen incoming messages, if the messageType
    // is LOAD then the game state will be loaded.
    // Note that no checking is done, whether the
    // gameState in the incoming message contains
    // correct information.
    //
    // Also handles any errors that the service
    // wants to send (displays them as an alert).
    window.addEventListener("message", function(evt)
    {
        if(evt.data.messageType === "LOAD")
        {
            scoreNumber = evt.data.gameState.score;
            $("#score").text(scoreNumber);
            speedFactor = evt.data.gameState.speedFactor;

            console.log('LOAD');
            console.log('score is: ', scoreNumber);
            console.log('speedFactor is: ', speedFactor);
        }
        else if (evt.data.messageType === "ERROR")
        {
            alert(evt.data.info);
        }
    });


    // Request the service to set the resolution of the
    // iframe correspondingly
    var message =
    {
        messageType: "SETTING",
        options:
        {
            "width": 650, //Integer
            "height": 500 //Integer
        }
    };
    window.parent.postMessage(message, "*");

});

var Component = function(args)
{
    this.x = args.x;
    this.y = args.y;
    this.dx = args.dx;
    this.dy = args.dy;
    this.radius = args.radius;
    this.color = args.color;

    //ctx.fillRect(this.x, this.y, this.width, this.height);
    /*
    this.update = function()
    {
        ctx.font = this.width + " " + this.height;
        ctx.fillStyle = color;
        ctx.fillText(this.text, this.x, this.y);
    }
    */
}

function keyDownHandler(e)
{
    if(e.keyCode == 87 || e.keyCode == 38)
    {
        upPressed = true;
    }
    else if(e.keyCode == 65 || e.keyCode == 37)
    {
        leftPressed = true;
    }
    else if(e.keyCode == 83 || e.keyCode == 40)
    {
        downPressed = true;
    }
    else if(e.keyCode == 68 || e.keyCode == 39)
    {
        rightPressed = true;
    }
}
function keyUpHandler(e) {
    if(e.keyCode == 87 || e.keyCode == 38)
    {
        upPressed = false;
    }
    else if(e.keyCode == 65 || e.keyCode == 37)
    {
        leftPressed = false;
    }
    else if(e.keyCode == 83 || e.keyCode == 40)
    {
        downPressed = false;
    }
    else if(e.keyCode == 68 || e.keyCode == 39)
    {
        rightPressed = false;
    }
}

function drawBall(ballObject)
{
    ctx.beginPath();
    ctx.arc(ballObject.x, ballObject.y, ballObject.radius,
    			0, Math.PI*2);
    ctx.fillStyle = ballObject.color;
    ctx.fill();
    ctx.closePath();

}


function drawSquare()
{
    ctx.beginPath();
    ctx.rect(squareX, squareY, squareWidth, squareHeight);
    ctx.fillStyle = "#B22222";
    ctx.fill();
    ctx.closePath();
}

function draw(ballObject)
{
    frameNumber += 1;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawBall(ballObject);
    drawSquare();
}

function handleBallTurn(ballObject)
{
    // ball handling
    if(ballObject.x + ballObject.dx > canvas.width-ballObject.radius ||
                ballObject.x + ballObject.dx < ballObject.radius)
    {
        ballObject.dx = -1*(ballObject.dx);
    }

    if(ballObject.y + ballObject.dy > canvas.height-ballObject.radius ||
                ballObject.y + ballObject.dy < ballObject.radius)
    {
        ballObject.dy = -1*(ballObject.dy);
    }


    ballObject.x += ballObject.dx * speedFactor;
    ballObject.y += ballObject.dy * speedFactor;


    if(( ballObject.x > squareX && ballObject.x < squareX + squareWidth ))
    {
        if(( ballObject.y > squareY && ballObject.y < squareY + squareHeight ))
        {
            //document.location.reload();
            pauseGame();
        }
    }
}

function handleSquareTurn()
{
    // square handling
    if(rightPressed && squareX < canvas.width-squareWidth)
    {
        squareX += squareSpeed;
    }
    else if(leftPressed && squareX > 0)
    {
        squareX -= squareSpeed;
    }
    else if(downPressed && squareY < canvas.height-squareHeight)
    {
        squareY += squareSpeed;
    }
    else if(upPressed && squareY > 0)
    {
        squareY -= squareSpeed;
    }
}


function handleScore()
{
    if (frameNumber > 100)
    {
        scoreNumber += 1;
        frameNumber = 0;
        levelCounter += 1;
        //addBall();
    }

    $("#score").text(scoreNumber);

    if (levelCounter > 2)
    {
        speedFactor *= speedIncrease;
        levelCounter = 0;
    }
}

function updateHandler()
{
    handleSquareTurn();
    for (var i = 0; i < balls.length; i++)
    {
        handleBallTurn(balls[i]);
        draw(balls[i]);
    }
    
    handleScore();
    if (!gameOver)
    {
        animationFrame = requestAnimationFrame(updateHandler);
    }
}

function addBall()
{
    var args =
    {
        color :  "#4169E1",
        x : canvas.width/2,
        y : canvas.height-30,
        dx : 2,
        dy : -2,
        radius : 15
    };

    var newBall = new Component(args);
    balls.push(newBall);
}

function startNewGame()
{
    cancelAnimationFrame(animationFrame);
    while(balls.length > 0)
    {
        balls.pop();
    }
    x = canvas.width/2;
    y = canvas.height-30;
    dx = 2;
    dy = -2;
    squareX = (canvas.width-squareWidth)/2;
    squareY = (canvas.height-squareHeight)/2;
    upPressed = false;
    downPressed = false;
    rightPressed = false;
    leftPressed = false;
    speedFactor = 1;
    squareSpeed = 6;
    frameNumber = 0;
    scoreNumber = 0;
    levelCounter = 0;
    var startTime = performance.now();
    balls = [];
    gameOver = false;

    document.addEventListener("keydown", keyDownHandler, false);
    document.addEventListener("keyup", keyUpHandler, false);

    addBall();

    updateHandler();
}

function pauseGame()
{
    gameOver = true;
}

startNewGame();
