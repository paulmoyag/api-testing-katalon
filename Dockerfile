pipeline {
  agent  { 
        dockerfile { 
              //dir 'Docker/kubernetes-cli' 
              args '-u 0:0' //Forces Container tu run as User Root                    
              reuseNode true
              label 'ec2-linux-spot-slave'
             }
          
         }
  
  parameters { 
    string(name: 'DEPLOY_TO', defaultValue: '', description: '') 
    string(name: 'DEPLOY_COMMIT', defaultValue: '', description: '') 
  }
  stages {
    stage('Start') {
      steps {
            notifyBuild('STARTED')      
        }
    }
    stage('Build') {
      steps {
            sh 'npm config set unsafe-perm true'
            sh 'npm install'
        }
    }
	
    stage('S3download Configuraciones') {
        steps {
            sh "aws s3 cp s3://belcorp-codedeploy/ProductAPI/Config/configuraciones.yml configuraciones.yml"
        }
    }		
	
    stage ('Deploy serveless QA ') {
	
	    when {
               expression { isStage() }
            }
			
      steps {
            sh 'npm install -g serverless@1.40.0'
            sh 'serverless deploy --stage qas --force'
        }
    }
	
    stage ('Deploy serveless PRD ') {
	
	    when {
               expression { enableDeploy() }
            }
			
      steps {
            sh 'npm install -g serverless@1.40.0'
            sh 'serverless deploy --stage prd --force --verbose'
        }
    }
	
  }
  post {
      always {
        notifyBuild(currentBuild.result)
      }
  }
}
def notifyBuild(String buildStatus = 'STARTED') {
    buildStatus = buildStatus ?: 'SUCCESS'
    String buildPhase = (buildStatus == 'STARTED') ? 'STARTED' : 'FINALIZED'
    commit = (buildStatus == 'STARTED') ? 'null' : sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'")
    
    sh """curl -H "Content-Type: application/json" -X POST -d '{
        "name": "${env.JOB_NAME}",
        "type": "pipeline",
        "build": {
            "phase": "${buildPhase}",
            "status": "${buildStatus}",
            "number": ${env.BUILD_ID},
            "scm": {
                "commit": "${commit}"
            },
            "artifacts": {}
        }
    }' https://devops.belcorp.biz/gestionar_despliegues_qa"""
}
def isMaster() {
  return env.BRANCH_NAME == "master"
}

def isStage() {
  return env.BRANCH_NAME == "qas"
}
def enableDeploy() {
  return isMaster() && params.DEPLOY_TO == 'production'
}
