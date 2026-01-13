pipeline{
    
    agent any
    
    stages{
        stage("Code Clone"){
            steps{
               script{
                 echo " clone("https://github.com/LondheShubham153/two-tier-flask-app.git", "master")"
               }
            }
        }
        stage("Trivy File System Scan"){
            steps{
                script{
                    trivy_fs()
                }
            }
        }
        stage("Build"){
            steps{
                sh "docker build -t two-tier-flask-app ."
            }
            
        }
        stage("Test"){
            steps{
                echo "Developer / Tester tests likh ke dega..."
            }
            
        }
        stage("Push to Docker Hub"){
            steps{
                script{
                    echo "docker_push("dockerHubCreds","two-tier-flask-app") "
                }  
            }
        }
        stage("Deploy"){
            steps{
                sh "docker compose up -d --build flask-app"
            }
        }
    }

