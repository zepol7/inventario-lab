// Pipeline CI/CD - Gestion del Software + Prueba y Calidad de Software
pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '15'))
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        VENV         = '.venv'
        PYTHONUTF8   = '1'
        COVERAGE_MIN = '85'
        AMBIENTES    = '/var/jenkins_home/ambientes'
    }

    stages {

        stage('Checkout') {                       // [Gestion] control de versiones
            steps {
                checkout scm
                sh 'git log -1 --pretty="%h %an: %s"'
                script {
                    env.VERSION = sh(
                        script: 'python3 -c "import sys; sys.path.insert(0, \'src\'); import inventario; print(inventario.__version__)"',
                        returnStdout: true
                    ).trim()
                    currentBuild.displayName = "#${env.BUILD_NUMBER} v${env.VERSION}"
                }
            }
        }

        stage('Preparar entorno') {               // [Gestion] entorno reproducible
            steps {
                sh '''
                    python3 -m venv $VENV
                    . $VENV/bin/activate
                    pip install -q --upgrade pip
                    pip install -q -r requirements-dev.txt
                    mkdir -p reports
                '''
            }
        }

        stage('Analisis estatico') {              // [Calidad] estandares de codigo
            parallel {
                stage('flake8') {
                    steps {
                        sh '. $VENV/bin/activate && python -m flake8 src tests --output-file=reports/flake8.txt --tee'
                    }
                }
                stage('pylint') {
                    steps {
                        sh '. $VENV/bin/activate && python -m pylint src/inventario --output-format=parseable --output=reports/pylint.txt --fail-under=8'
                    }
                }
            }
        }

        stage('Seguridad') {                      // [Calidad] SAST + dependencias
            steps {
                sh '. $VENV/bin/activate && python -m bandit -r src -f txt -o reports/bandit.txt --severity-level medium'
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '. $VENV/bin/activate && python -m pip_audit -r requirements-dev.txt'
                }
            }
        }

        stage('Pruebas unitarias') {              // [Calidad] nivel unitario
            steps {
                sh '''
                    . $VENV/bin/activate
                    python -m pytest tests/unit --junitxml=reports/junit-unit.xml \
                        --cov --cov-report=
                '''
            }
        }

        stage('Pruebas de integracion') {         // [Calidad] nivel integracion + umbral
            steps {
                sh '''
                    . $VENV/bin/activate
                    python -m pytest tests/integration --junitxml=reports/junit-integration.xml \
                        --cov --cov-append --cov-report=xml:reports/coverage.xml \
                        --cov-fail-under=$COVERAGE_MIN
                '''
            }
        }

        stage('SonarQube') {                      // [Calidad] metricas e indicadores
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectVersion=${env.VERSION}"
                    }
                }
            }
        }

        stage('Quality Gate') {                   // [Calidad] criterio de aceptacion
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Construir paquete') {              // [Gestion] build + artefacto
            steps {
                sh '. $VENV/bin/activate && python -m build'
                archiveArtifacts artifacts: 'dist/*', fingerprint: true
            }
        }

        stage('Desplegar a staging') {            // [Gestion] ambiente de pruebas
            when { branch 'develop' }
            steps { desplegar('staging') }
        }

        stage('Desplegar a produccion') {         // [Gestion] liberacion controlada
            when { branch 'main' }
            input {
                message '¿Aprobar despliegue a produccion?'
                ok 'Desplegar'
            }
            steps {
                desplegar('produccion')
                withCredentials([gitUsernamePassword(credentialsId: 'github-token', gitToolName: 'Default')]) {
                    sh '''
                        if git ls-remote --exit-code --tags origin "v$VERSION"; then
                            echo "La version v$VERSION ya existe: sube la version en src/inventario/__init__.py"
                            exit 1
                        fi
                        git tag -a "v$VERSION" -m "Release v$VERSION (build $BUILD_NUMBER)"
                        git push origin "v$VERSION"
                    '''
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/junit-*.xml'
            recordCoverage(tools: [[parser: 'COBERTURA', pattern: 'reports/coverage.xml']])
            recordIssues(enabledForFailure: true, tools: [
                flake8(pattern: 'reports/flake8.txt'),
                pyLint(pattern: 'reports/pylint.txt')
            ])
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        success  { echo "OK: v${env.VERSION} en ${env.BRANCH_NAME}" }
        unstable { echo 'Inestable: revisar advertencias de seguridad o calidad' }
        failure  { echo 'Fallo: revisar la etapa en rojo y sus reportes' }
        cleanup  { cleanWs() }
    }
}

// Instala el paquete construido en un venv por ambiente y ejecuta un smoke test
def desplegar(String ambiente) {
    sh """
        rm -rf ${AMBIENTES}/${ambiente}
        python3 -m venv ${AMBIENTES}/${ambiente}
        ${AMBIENTES}/${ambiente}/bin/pip install -q dist/*.whl
        ${AMBIENTES}/${ambiente}/bin/python -c "import inventario; print('Smoke test OK - v' + inventario.__version__)"
        echo "v${VERSION} desplegada en ${ambiente}"
    """
}
