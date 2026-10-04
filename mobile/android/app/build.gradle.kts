import java.util.Properties

plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

// La firma di rilascio: android/key.properties (ignorato da git) punta al keystore di upload, che sta fuori dal repo
// con una copia di sicurezza a parte. Senza quel file la build di rilascio si firma con la chiave di debug, solo per prova.
val proprietaFirma = Properties().apply {
    val file = rootProject.file("key.properties")
    if (file.exists()) file.inputStream().use { load(it) }
}

android {
    namespace = "chat.tarots.app"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
        // Fase 9: flutter_local_notifications usa le API java.time anche sui telefoni vecchi (desugaring).
        isCoreLibraryDesugaringEnabled = true
    }

    defaultConfig {
        // Lo stesso identificativo su Android e iOS.
        applicationId = "chat.tarots.app"
        // flutter_appauth chiede almeno Android 7.0 (API 24).
        minSdk = maxOf(24, flutter.minSdkVersion)
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
        // Il ritorno dall'accesso con Keycloak: chat.tarots.app:/oauth2redirect (flutter_appauth).
        manifestPlaceholders["appAuthRedirectScheme"] = "chat.tarots.app"
    }

    signingConfigs {
        if (proprietaFirma.containsKey("storeFile")) {
            create("upload") {
                storeFile = file(proprietaFirma.getProperty("storeFile"))
                storePassword = proprietaFirma.getProperty("storePassword")
                keyAlias = proprietaFirma.getProperty("keyAlias")
                keyPassword = proprietaFirma.getProperty("keyPassword")
            }
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.findByName("upload") ?: signingConfigs.getByName("debug")
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}

dependencies {
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")
}
