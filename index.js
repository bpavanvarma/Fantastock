// dashboard setup
function getDetails(){
    const access_token = localStorage.getItem("access_token"); // NEW
    console.log(access_token); // NEW
    var apigClient = apigClientFactory.newClient({ apiKey: "YGYREcyKsh2vbajRUEkBa7I8OTnjDFUh8hNiKSze" });
      var body = {
          "token":access_token
      };
      var params = { };
      var additionalParams = {headers:{
      'Content-Type':"application/json"
      }};
      apigClient.dashboardDetailsPost(params, body, additionalParams).then(function(res){
          createDashboard(res.data)
        }).catch(function(result){
          // console.log(result)
          // createDashboard(result.data)
            console.log("NO RESULT");
        });
    }



  function createDashboard(result){
    // console.log(result);
    result=result.body

    current_coins=result['coins']
    current_competitions=result['competitions']
    app_doj=result['dateofjoin']
    current_name=result['name']

    var toAdd = document.createDocumentFragment();
    //main details
    var detailDiv=document.createElement("div");
    detailDiv.setAttribute('class', 'componentWrapper');

    var header=document.createElement("div");
    header.setAttribute('class', 'header');
    header.innerHTML="YOUR MAIN STATISTICS";
    detailDiv.appendChild(header);

    var nameDiv=document.createElement('div');
    nameDiv.setAttribute('class', "detail");
    nameDiv.innerHTML="USERNAME : "+current_name;
    detailDiv.appendChild(nameDiv);

    var joindt=document.createElement('div');
    joindt.setAttribute('class', "detail");
    joindt.innerHTML="MEMBER SINCE : "+app_doj;
    detailDiv.appendChild(joindt);

    var coinDiv=document.createElement('div');
    coinDiv.setAttribute('class', "detail");
    coinDiv.innerHTML="YOU CURRENTLY HAVE : "+current_coins+" coins";
    detailDiv.appendChild(coinDiv);


    var count = 0;
    for (var i in current_competitions) {
       if(current_competitions.hasOwnProperty(i)){
          count++;
        }
    }

    var competitions=document.createElement('div');
    competitions.setAttribute('class', "detail");
    competitions.innerHTML="TOTAL COMPETITIONS PARTICIPATED : "+count;
    detailDiv.appendChild(competitions);


    toAdd.appendChild(detailDiv);

    //now competition stocks
    for (var key in current_competitions){
      var competition=document.createElement('div');
      competition.setAttribute("class", "setCompetitions");

      var cname=document.createElement('div');
      cname.setAttribute('class', "subdetail1");
      cname.innerHTML="COMPETITION NAME -->"+key;
      competition.appendChild(cname);


      tbl = document.createElement('table');
      tbl.setAttribute("class", "zui-table");
      tbl.style.width = '500px';
      tbl.style.border = '1px solid black';

      comp=current_competitions[key]
      var rank=comp['rank']
      var stocks=comp['stocks']

    //   //append rank
      rankDiv=document.createElement('div');
      rankDiv.setAttribute('class', 'subdetail2');
      rankDiv.innerHTML="Rank in this competition : "+rank.toString();

      console.log(rank, stocks)
      //stocks
      for (let i = 0; i < 5; i++) {
        const tr = tbl.insertRow();
        const td = tr.insertCell();
        td.appendChild(document.createTextNode((i+1).toString()+". "+stocks[i]));
        console.log(stocks[i]);
      }

      competition.appendChild(rankDiv);
      competition.appendChild(tbl);

    //   //push to fragment
      toAdd.appendChild(competition)
      }

    document.getElementById("dashboard_info").appendChild(toAdd);
  }


///// GET COMPETITIONS TRIGGER //////

function getCompetitions() {
  var apigClient = apigClientFactory.newClient({ apiKey: "YGYREcyKsh2vbajRUEkBa7I8OTnjDFUh8hNiKSze" });
    var body = { };
    var params = { };
    var additionalParams = {headers:{
    'Content-Type':"application/json"
    }};
    apigClient.competitionsGet(params, body , additionalParams).then(function(res){
        console.log("success");
        showCompetitions(res.data)
      }).catch(function(result){
          console.log(result);
          console.log("NO RESULT");
      });
}


/////// SHOW COMPETITIONS BY SEARCH //////

function showCompetitions(res) {
  if (res.length == 0) {
    var newContent = document.createTextNode("No competitions to display");
    newDiv.appendChild(newContent);
  }
  else {
    results=res.body;
    var toAdd = document.createDocumentFragment();
    for (var i = 0; i < results.length; i++) {
       console.log(results[i])
       var newDiv = document.createElement('div');
       newDiv.id = results[i]['Competitionid'];
       // newDiv.innerHTML += results[i]['CompetitionId']+"--->"+results[i]['status'];
       newDiv.className = 'competition_class';
       //setting onclick
       if((results[i]['status']==='LIVE')||(results[i]['status']==='Live')){
         newDiv.setAttribute('onclick', "util();");
       }else{
         newDiv.setAttribute('onclick', "getCompetitionDetails(this.id);");
       }
       

       //setting the competition name
       var competion_name=document.createElement('div');
       competion_name.className='competion_name';
       competion_name.innerHTML+=results[i]['Competitionid']
       newDiv.appendChild(competion_name)
       
       //setting the pool size
       var poolSize=document.createElement('div');
       poolSize.className='pool_size';
       poolSize.innerHTML+="Pool size : "+results[i]['attributes'].poolsize
       newDiv.appendChild(poolSize)

       // setting total winners
       var winners=document.createElement('div');
       winners.className='winners_size';
       winners.innerHTML+="Total Winners: "+results[i]['attributes'].winners
       newDiv.appendChild(winners)
       
       // //setting total money that can be won
       var t_amt=document.createElement('div');
       t_amt.className='amount_to_win';
       t_amt.innerHTML+=results[i]['type']+" -- "+results[i]['attributes'].totalamount
       newDiv.appendChild(t_amt)
       
       //setting status
       var status=document.createElement('div');
       status.className='status';
       status.innerHTML+= "Status: "+results[i]['status']
       if((results[i]['status']==='LIVE') || (results[i]['status']==='Live') || (results[i]['status']==='live')){
        status.setAttribute("style", "background-color: green;")
       }else{
        status.setAttribute("style", "background-color: red;")
       }
       newDiv.appendChild(status)


       //adding everything to toAdd frame
       toAdd.appendChild(newDiv);

    }
    document.getElementById("competitions_list").appendChild(toAdd);
  }
}


  function util(){
    alert("Sorry, the competition is already started! Please monitor your dashboard for the results if you have registered!");
  }

///// SHOW THE COMPETITION WITH COMPANIES TO SELECT TO BE RETRIEVED AFTER LF4 is created ///////

  function getCompetitionDetails(competiton){
    window.location.href='companies_page.html?competition='+competiton;
  }

  function fetchCompetitionDetails(){
    var params = new URLSearchParams(document.location.search);
    var competiton = params.get("competition");

    const access_token = localStorage.getItem("access_token"); // NEW
    console.log(access_token); // NEW

    var apigClient = apigClientFactory.newClient({ apiKey: "YGYREcyKsh2vbajRUEkBa7I8OTnjDFUh8hNiKSze" });
    var body = {
      "competition":competiton,
      "token":access_token // NEWWW
    };
    var params = {};
    var additionalParams = {headers: {
    'Content-Type':"application/json"
    }};
    apigClient.competitionDetailsPost(params, body , additionalParams).then(function(res){
        showCompetitionDetails(res.data)
      }).catch(function(result){
          console.log(result);
          console.log("NO RESULT");
      });
  }


function showCompetitionDetails(res) {
  if (res.length == 0) {
    var newContent = document.createTextNode("No Companies to display");
    newDiv.appendChild(newContent);
    console.log("HERE I AM NOT COMPLETE")
  }
  else {
    results=res.body;

    var toAdd = document.createDocumentFragment();
    //create a form
    var form = document.createElement("form");
        form.setAttribute("method", "post");
        form.setAttribute('class', 'form_company')

    //create a loop to input companies in the form
    for (var i = 0; i < 11; i++) {

        var slot=document.createElement("div");
        slot.setAttribute('class', 'company_name')

        
        var company=document.createElement('div');

        var companySlot = document.createElement("INPUT");
        companySlot.setAttribute("type", "checkbox");
        companySlot.setAttribute("id", "company"+i.toString());
        companySlot.setAttribute("class", results[i]);


        company.appendChild(companySlot);
        company.innerHTML+=results[i];
        company.setAttribute("class", "companyName")

        slot.appendChild(company)
        form.append(slot)
    }
    var s = document.createElement('div');
       s.className = 'SubmitButton';
       s.innerHTML = "SUBMIT"
       s.setAttribute('onclick', "submitFormelements();")

    form.append(s); 

    toAdd.appendChild(form)
    document.getElementById("company_list").appendChild(toAdd);

    }
  }



//// GET THE USER INFORMATION ONTO THE DASHBOARD ///////////

  function getUserInformation(userName){
    var apigClient = apigClientFactory.newClient({ apiKey: "YGYREcyKsh2vbajRUEkBa7I8OTnjDFUh8hNiKSze" });
    var body = {};
    var params = {};
    var additionalParams = {headers: {
    'Content-Type':"application/json"
    }};
    apigClient.userDetailsUserGet(params, body , additionalParams).then(function(res){
        console.log("success");
        showCompetitions(res.data)
      }).catch(function(result){
          console.log(result);
          console.log("NO RESULT");
      });
  }



  ///////// SUBMIT ALL THE FORM ELEMENTS ///////////
  
  function submitFormelements(){
    company=[]
    for (var i = 0; i < 11; i++) {
        if(document.getElementById('company'+i.toString()).checked){
          company.push(document.getElementById('company'+i.toString()).className)
        }
    }

    if(company.length<5){
      alert("Please Select Atleast 5 Stocks");
    }
    else if(company.length>5){
      alert("Please Select Only 5 Stocks");
    }

    else{
      
      console.log("HERE I AMMMMIN SELECTION");

      const access_token = localStorage.getItem("access_token"); // NEW
      console.log(access_token); // NEW

      var params = new URLSearchParams(document.location.search);
      var competiton = params.get("competition");

      var apigClient = apigClientFactory.newClient({ apiKey: "YGYREcyKsh2vbajRUEkBa7I8OTnjDFUh8hNiKSze" });
      var body = {
        "companies":company,
        "competition":competiton,
        "token":access_token // NEWWW
        
      };
      var params = {};
      var additionalParams = {headers: {
      'Content-Type':"application/json"
      }};
      apigClient.competitionEntryPost(params, body , additionalParams).then(function(res){
          alert("Congratulations! You just registered to the competition!!");
          window.location.href='dashboard.html';
        }).catch(function(result){
            console.log(result);
            console.log("NO RESULT");
        });
    }
  }
