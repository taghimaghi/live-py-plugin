plugins {
    id("java")
    id("org.jetbrains.intellij") version "1.13.3"
}

group = "io.github.donkirkby"
version = "4.10.2"

repositories {
    mavenCentral()
}

// Configure Gradle IntelliJ Plugin
// Read more: https://plugins.jetbrains.com/docs/intellij/tools-gradle-intellij-plugin.html
intellij {
    version.set("231.9011.34")
    type.set("IC") // Target IDE Platform: IU for Ultimate, IC for community

    // Pythonid for Ultimate, PythonCore for community
    plugins.set(listOf("PythonCore:231.8770.65"))
}

sourceSets {
    main {
        java {
            setSrcDirs(listOf("src/main/java"))
        }
        resources {
            setSrcDirs(listOf("src/main/resources", "../plugin/PySrc"))
        }
    }
    test {
        java {
            setSrcDirs(listOf("src/test"))
        }
    }
}

tasks {
    // Set the JVM compatibility versions
    withType<JavaCompile> {
        sourceCompatibility = "11"
        targetCompatibility = "11"
    }

    patchPluginXml {
        sinceBuild.set("212.4746.92")
        untilBuild.set("")
    }

    runPluginVerifier {
        // Verify against sinceBuild version and current version.
        ideVersions.set(listOf<String>("212.4746.92", "232.6095.10"))
    }

    signPlugin {
        certificateChain.set(System.getenv("CERTIFICATE_CHAIN"))
        privateKey.set(System.getenv("PRIVATE_KEY"))
        password.set(System.getenv("PRIVATE_KEY_PASSWORD"))
    }

    publishPlugin {
        token.set(System.getenv("PUBLISH_TOKEN"))
    }
}
