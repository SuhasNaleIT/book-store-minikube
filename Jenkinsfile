pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: docker
    image: docker:24-dind
    securityContext:
      privileged: true
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
    volumeMounts:
    - name: docker-graph-storage
      mountPath: /var/lib/docker
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ['cat']
    tty: true
  volumes:
  - name: docker-graph-storage
    emptyDir: {}
"""
            defaultContainer 'docker'
        }
    }

    environment {
        DOCKER_HUB_USER = 'YOUR_DOCKERHUB_USERNAME'
        APP_IMAGE       = "${DOCKER_HUB_USER}/app-service:${BUILD_NUMBER}"
        CATALOGUE_IMAGE = "${DOCKER_HUB_USER}/catalogue-service:${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Pulling latest code...'
                checkout scm
            }
        }

        stage('Build Images') {
            steps {
                echo 'Building Docker images...'
                sh """
                    docker build -t ${APP_IMAGE} ./app-service
                    docker build -t ${CATALOGUE_IMAGE} ./catalogue-service
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push ${APP_IMAGE}
                        docker push ${CATALOGUE_IMAGE}
                    """
                }
            }
        }

        stage('Deploy to Kubernetes') {
            container('kubectl') {
                steps {
                    echo 'Deploying to Kubernetes...'
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        sh """
                            kubectl set image deployment/app-service \
                                app-service=${APP_IMAGE} -n bookstore

                            kubectl set image deployment/catalogue-service-blue \
                                catalogue-service=${CATALOGUE_IMAGE} -n bookstore
                        """
                    }
                }
            }
        }

        stage('Verify Deployment') {
            container('kubectl') {
                steps {
                    echo 'Verifying pods...'
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        sh """
                            kubectl rollout status deployment/app-service -n bookstore
                            kubectl rollout status deployment/catalogue-service-blue -n bookstore
                        """
                    }
                }
            }
        }
    }

    post {
        success { echo '✅ Pipeline completed successfully!' }
        failure { echo '❌ Pipeline failed — check logs above.' }
    }
}