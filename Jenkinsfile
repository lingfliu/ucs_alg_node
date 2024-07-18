pipeline {
    agent any

    triggers {
        // 定义轮询触发器，这里设置为每5分钟检查一次代码更新
        pollSCM('*/5 * * * *')
    }

    environment {
	    // GIT地址
        GIT_URL = 'https://e.coding.net/lingfliu/ucs/ucs_alg_node_service.git'
	    // 版本信息，用当前时间
        VERSION = VersionNumber versionPrefix: 'prod.', versionNumberString: '${BUILD_DATE_FORMATTED, "yyyyMMdd"}.${BUILDS_TODAY}'
        GIT_URL_WITH_AUTH = 'https://hjk:1baffd762ce9869ca4a1d62c85259bdda4c57d7c@e.coding.net/lingfliu/ucs/ucs_alg_node_service.git'
    }
    
    parameters {
        choice(
		name: 'OP',
		choices: 'publish\nrollback', 
		description: 'publish(发布新版本时选择，部署后自动生成新tag) rollback(回滚时选择，需要同时选择回滚的tag)'
	    )

        choice(
		name: 'DEPLOYENV', 
		choices: 'prod\ntest', description: 'prod(部署环境) test(测试环境)'
	    )

        gitParameter(
		branch: '', 
		branchFilter: 'origin/(.*)', 
		defaultValue: 'master', 
		description: '选择将要构建的标签', 
		name: 'TAG', 
		quickFilterEnabled: false, 
		selectedValue: 'TOP',
		sortMode: 'DESCENDING_SMART', 
		tagFilter: '*',
		type: 'PT_TAG', 
		useRepository: env.GIT_URL
	    )

        string(
            name: 'REMOTE_DIR', 
            defaultValue: '/home/springboot_2',
            description: '远程部署目录'
        )

        string(
            name: 'EXEC_COMMAND', 
            defaultValue: 'nohup sh /home/springboot_2/test.sh', 
            description: '远程部署执行脚本'
        )
    }

    stages {
        stage('拉取代码') {
            steps {
		        // 清除工作空间并拉取最新的代码
                cleanWs()
                // 使用 git 插件拉取代码
                script {
                    if (params.OP == 'publish') {
                        // 如果是发布操作，则拉取 master 分支的最新代码
                        checkout([$class: 'GitSCM', branches: [[name: '*/master']], userRemoteConfigs: [[url: "${env.GIT_URL}"]]])
                    } else if (params.OP == 'rollback') {
                        // 如果是回滚操作，则拉取指定的 tag
                        checkout([$class: 'GitSCM', branches: [[name: "${params.TAG}"]], userRemoteConfigs: [[url: "${env.GIT_URL}"]]])
                    }
                }
            }
        }
        
        stage('代码打包') {
            steps {
                echo '前后端团队编写docker compose'
            }
        }
        
        stage('远程部署项目') {
            steps {
                sshPublisher(
                    publishers: [
                        sshPublisherDesc(
                            configName: '123.60.173.147', 
                            transfers: [
                                sshTransfer(
                                    cleanRemote: false,
                                    excludes: '', 
                                    execCommand: params.EXEC_COMMAND, 
                                    execTimeout: 120000, 
                                    flatten: false, 
                                    makeEmptyDirs: false, 
                                    noDefaultExcludes: false, 
                                    patternSeparator: '[, ]+', 
                                    remoteDirectory: params.REMOTE_DIR, 
                                    remoteDirectorySDF: false, 
                                    removePrefix: '', sourceFiles: '*'
                                )
                            ],
                            usePromotionTimestamp: false, 
                            useWorkspaceInPromotion: false, 
                            verbose: false
                        )
                    ]
                )
            }
        }

        stage('新版本打tag') {
            steps {
                // 执行脚本步骤来打标签并推送
                script {
                    // 打标签
                    sh 'git tag ' + env.VERSION
                    // 推送标签至远程仓库
                    sh 'git push ' + env.GIT_URL_WITH_AUTH + ' ' + env.VERSION
                }
            }
        }
    }
}
