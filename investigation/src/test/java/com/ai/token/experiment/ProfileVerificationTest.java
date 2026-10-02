package com.ai.token.experiment;

import java.nio.file.*;
import java.util.Arrays;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import org.springframework.boot.*;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.core.OutputStreamAppender;
import ch.qos.logback.classic.encoder.PatternLayoutEncoder;
import org.slf4j.LoggerFactory;

/** Separate setup probe; its output never becomes failure.log. */
@Tag("investigation")
class ProfileVerificationTest {
    @Test void effectiveProfile() throws Exception {
        var boot = new SpringApplication(FailureCasesTest.Empty.class);
        boot.setWebApplicationType(WebApplicationType.NONE);
        try (var context = boot.run()) {
            String requested = System.getProperty("spring.profiles.active", "");
            String active = String.join(",", context.getEnvironment().getActiveProfiles());
            assertEquals(requested, active);
            var root = (Logger) LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME);
            var appender = (OutputStreamAppender<?>) root.getAppender("CONSOLE");
            assertNotNull(appender);
            String pattern = ((PatternLayoutEncoder) appender.getEncoder()).getPattern();
            if (requested.equals("agent")) {
                assertTrue(pattern.contains("%replace(%wEx)"));
                assertTrue(pattern.contains("[%thread]"));
            } else {
                assertFalse(pattern.contains("%replace(%wEx)"));
            }
            Path file = Path.of(System.getProperty("experiment.profileArtifact", "target/profile-verification.txt"));
            Files.writeString(file, "requested=" + requested + "\nactive=" + active + "\nappender=" + appender.getName() + "\npattern=" + pattern + "\n");
        }
    }
}
