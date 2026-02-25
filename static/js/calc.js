function calsum500() {
    let a = document.getElementById("n500").value;
    let b = a * 500;
    document.getElementById("na500").value = b;
}
function calsum200() {
    let a = document.getElementById("n200").value;
    let b = a * 200;
    document.getElementById("na200").value = b;
}
function calsum100() {
    let a = document.getElementById("n100").value;
    let b = a * 100;
    document.getElementById("na100").value = b;
}
function calsum50() {
    let a = document.getElementById("n50").value;
    let b = a * 50;
    document.getElementById("na50").value = b;
}
function calsum() {
    let a = parseInt(document.getElementById("na500").value) || 0;
    let b = parseInt(document.getElementById("na200").value) || 0;
    let c = parseInt(document.getElementById("na100").value) || 0;
    let d = parseInt(document.getElementById("na50").value) || 0;
    let re = a + b + c + d;
    document.getElementById("dp").value = re;
}
function deposit1() {
    alert("Money has been successfully added to your account after admin's approval!...")
}
function withdraw1() {
    alert("Money has been successfully Withdrawn!...");
}
function showForm() {
    if (document.getElementById("r1").style.display === "none") {
        document.getElementById("r1").style.display = "block";
    }
    else{
        document.getElementById("r1").style.display="none";
    }
}
function showdeposit()
{
    if(document.getElementById("dp23").style.display==="none")
    {
        document.getElementById("dp23").style.display="block";
        document.getElementById("wd23").style.display="none";
    }
    else{
        document.getElementById("dp23").style.display="none";
    }
}
function showwithdraw()
{
    if(document.getElementById("wd23").style.display==="none"){
        document.getElementById("wd23").style.display="block";
        document.getElementById("dp23").style.display="none";
    }
    else{
        document.getElementById("wd23").style.display="none";
    }
}
function showloanpay()
{
    if(document.getElementById("ld1").style.display==="none")
    {
        document.getElementById("ld1").style.display="block";
    }
    else{
        document.getElementById("ld1").style.display="none";
    }
}
function loanreq(){
    alert("The Loan is applied successfully....")
}