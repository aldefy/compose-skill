plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "dev.aditlal.composeskill.verify"
    compileSdk = 35

    defaultConfig { minSdk = 24 }

    buildFeatures { compose = true }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }

    testOptions {
        unitTests {
            isIncludeAndroidResources = true
            isReturnDefaultValues = true
        }
    }
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2024.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.material3:material3")

    testImplementation(platform("androidx.compose:compose-bom:2024.10.01"))
    testImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.robolectric:robolectric:4.14")
    testImplementation("androidx.test.ext:junit:1.2.1")
}

val generateClaimTests = tasks.register<GenerateClaimTests>("generateClaimTests") {
    markdownFiles.set(listOf(
        rootProject.file("skills/compose-expert/references/modifiers.md"),
        rootProject.file("skills/compose-expert/references/pr-review.md"),
    ))
    outputDir.set(layout.buildDirectory.dir("generated/claim-tests"))
}

android.sourceSets.getByName("test").java.srcDir(
    layout.buildDirectory.dir("generated/claim-tests"),
)

tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile>().configureEach {
    if (name.contains("UnitTest")) dependsOn(generateClaimTests)
}
