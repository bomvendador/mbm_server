

    // document.addEventListener("DOMContentLoaded", function(event) {
    //   var devMode = $('#devMode').html()
    //   console.log('devMode  = ' + devMode)
    //   if (checkLocalVar()){
    //     if(devMode === 'true'){
    //       // google.script.run
    //       //   .withSuccessHandler(function(url){
    //       //     window.open(url + '?v=panel', '_top');
    //       //   })
    //       //   .getScriptUrl()
    //
    //
    //       window.open('https://script.google.com/macros/s/AKfycbw83yAMOQ7hfp-Bq-ACeeniBoQCt1OQ6P0iY_lcm_I/dev?v=panel', '_top');
    //     }else{
    //
    //       google.script.run
    //         .withSuccessHandler(function(url){
    //           window.open(url + '?v=panel', '_top');
    //         })
    //         .getScriptUrl()
    //
    //
    //     }
    //   }
    //
    // });


      function checkLocalVar(){
        if (sessionStorage.user_email){
          return true
        }
      }

      function setLocalVar(){
          if (!sessionStorage.user_email){

          window.sessionStorage.setItem("user_email", document.getElementById("inputEmail").value);
          console.log('new email saved - ' + sessionStorage.user_email);
          } else if(sessionStorage.user_email !== document.getElementById("inputEmail").value){
              sessionStorage.removeItem("user_email");
              window.sessionStorage.setItem("user_email", document.getElementById("inputEmail").value);
              console.log('email saved - ' + sessionStorage.user_email);

          }

      }


      document.getElementById("btn-submit").addEventListener("click", function(e){
          e.preventDefault();
          var data = {};
          var devMode = $('#devMode').html()
          data.user_login = document.getElementById("inputEmail").value;
          data.password = document.getElementById("inputPassword").value;
          document.getElementById('btn-submit').innerHTML = "<div class=='d-flex justify-content-center'><div class='spinner-border' style='width: 25px; height: 25px;' role='status'><span class='visually-hidden'>Loading...</span></div></div>"
          google.script.run.withFailureHandler(function(error){
              console.log("ошибка -" + error);
          }).withSuccessHandler(function(data){
              console.log("access = " + data);

              if(data){
                setLocalVar();
                //showAlert('alert-success', "User опознан", "alert-success-text");
                if(devMode === 'true'){
                  window.open('https://script.google.com/macros/s/AKfycbw83yAMOQ7hfp-Bq-ACeeniBoQCt1OQ6P0iY_lcm_I/dev?v=panel', '_top');
                }else{

                  google.script.run
                    .withSuccessHandler(function(url){
                      window.open(url + '?v=panel', '_top');
                    })
                    .getScriptUrl()


                  //window.open('https://script.google.com/macros/s/AKfycbzvAaa8ubiTzDlxQRrWYqTnbKKOIPRYfjJ0jZM7YQ7CGxHUNnBsbEML/exec?v=panel', '_top');
                }



///                window.open('https://script.google.com/macros/s/AKfycbzvAaa8ubiTzDlxQRrWYqTnbKKOIPRYfjJ0jZM7YQ7CGxHUNnBsbEML/exec?v=panel', '_top');
                //window.open('https://script.google.com/macros/s/AKfycbw83yAMOQ7hfp-Bq-ACeeniBoQCt1OQ6P0iY_lcm_I/dev?v=panel', '_top');

                /*
                google.script.run.withFailureHandler(function(error){
                  console.log(error);

                  showAlert("alert-warn", error, "alert-warn-text");
                }).withSuccessHandler(function(htmlOutput){

                  //window.document.querySelector('html').innerHTML = htmlOutput;
                  window.open('https://script.google.com/macros/s/AKfycbw83yAMOQ7hfp-Bq-ACeeniBoQCt1OQ6P0iY_lcm_I/dev?v=panel', '_top');
                }).getPageHtml('main_panel/html/base', sessionStorage.user_email);
                */

                //console.log(window.location + "?v=panel");
                //document.getElementById('btn-submit').innerHTML = "Войти"
              } else{
                showAlert("alert-warn", "Пароль или логин неверны", "alert-warn-text");
                document.getElementById('btn-submit').innerHTML = "Войти"

              }

          }).checkUser(data);

      });

      console.log('email - ' + sessionStorage.user_email);
