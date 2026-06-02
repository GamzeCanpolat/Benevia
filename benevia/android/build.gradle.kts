// ================================
// ROOT: android/build.gradle.kts
// ================================

// Firebase Google Services plugin (ROOT LEVEL)
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath("com.google.gms:google-services:4.4.2")
    }
}

// Make sure all modules use correct repos
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

// Set custom build directory (Flutter standard override)
val newBuildDir: Directory =
    rootProject.layout.buildDirectory
        .dir("../../build")
        .get()

rootProject.layout.buildDirectory.value(newBuildDir)

subprojects {
    val newSubprojectBuildDir: Directory = newBuildDir.dir(project.name)
    project.layout.buildDirectory.value(newSubprojectBuildDir)
}

// Required by Flutter Gradle system
subprojects {
    project.evaluationDependsOn(":app")
}

// Clean task
tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
