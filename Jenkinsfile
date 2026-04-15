pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: builder
    image: alpine/k8s:1.29.2
    command: ['cat']
    tty: true
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
    - name: workspace-volume
      mountPath: /home/jenkins/agent
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
  - name: workspace-volume
    emptyDir: {}
"""
            defaultContainer 'builder'
        }
    }

    environment {
        DOCKER_HUB_USER = 'c5053699'
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
                        echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                        docker push ${APP_IMAGE}
                        docker push ${CATALOGUE_IMAGE}
                    """
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh """
                        kubectl --kubeconfig=\$KUBECONFIG \
                            --server=https://kubernetes.default.svc \
                            --insecure-skip-tls-verify=true \
                            set image deployment/app-service \
                            app-service=${APP_IMAGE} -n bookstore

                        kubectl --kubeconfig=\$KUBECONFIG \
                            --server=https://kubernetes.default.svc \
                            --insecure-skip-tls-verify=true \
                            set image deployment/catalogue-service-blue \
                            catalogue-service=${CATALOGUE_IMAGE} -n bookstore
                    """
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh """
                        kubectl --kubeconfig=\$KUBECONFIG \
                            --server=https://kubernetes.default.svc \
                            --insecure-skip-tls-verify=true \
                            rollout status deployment/app-service -n bookstore

                        kubectl --kubeconfig=\$KUBECONFIG \
                            --server=https://kubernetes.default.svc \
                            --insecure-skip-tls-verify=true \
                            rollout status deployment/catalogue-service-blue -n bookstore
                    """
                }
            }
        }
    }

    post {
        success { echo '✅ Pipeline completed successfully!' }
        failure { echo '❌ Pipeline failed — check logs above.' }
    }
}