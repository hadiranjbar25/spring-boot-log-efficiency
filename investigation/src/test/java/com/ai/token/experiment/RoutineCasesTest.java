package com.ai.token.experiment;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import org.slf4j.*;
import org.springframework.boot.*;
import org.springframework.context.annotation.*;
import org.springframework.context.ConfigurableApplicationContext;
import java.util.stream.Stream;
import java.net.*;
import java.net.http.*;
import java.nio.charset.StandardCharsets;
import java.sql.*;
import java.time.Duration;
import com.sun.net.httpserver.HttpServer;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.wait.strategy.Wait;

@Tag("investigation")
class RoutineCasesTest {
    final RoutineService app = new RoutineService();
    static final Logger LOG = LoggerFactory.getLogger(RoutineService.class);
    @Configuration(proxyBeanMethods=false) static class Config {
        @Bean String serviceName() { return "orders"; }
    }
    ConfigurableApplicationContext context;
    @BeforeEach void start() {
        if (!System.getProperty("experiment.scenario", "unit").equals("unit")) {
            var boot = new SpringApplication(Config.class);
            boot.setWebApplicationType(WebApplicationType.NONE);
            context = boot.run();
        }
    }
    @AfterEach void stop() { if (context != null) context.close(); }
    void routine() {
        LOG.info("refresh completed request=refresh-7 records=12 status=ok");
        LOG.warn("inventory cache stale request=refresh-7 age=61s threshold=60s fallback=database");
    }
    @TestFactory Stream<DynamicTest> checks() {
        return switch (System.getProperty("experiment.scenario", "unit")) {
            case "unit" -> Stream.of(
                DynamicTest.dynamicTest("quantity pricing", () -> assertEquals(30, app.total(10, 3))),
                DynamicTest.dynamicTest("zero quantity", () -> assertEquals(0, app.total(8, 0))));
            case "integration" -> Stream.of(DynamicTest.dynamicTest("context and refresh", () -> {
                assertEquals("orders", context.getBean("serviceName"));
                assertEquals(30, app.total(10,3)); routine();
            }));
            case "http" -> Stream.of(DynamicTest.dynamicTest("request price", () -> {
                var server = HttpServer.create(new InetSocketAddress("127.0.0.1",0),0);
                server.createContext("/price", exchange -> {
                    byte[] body = Integer.toString(app.total(10,3)).getBytes(StandardCharsets.UTF_8);
                    exchange.getResponseHeaders().set("Content-Type","text/plain");
                    exchange.getResponseHeaders().set("X-Request-Id","http-7");
                    exchange.sendResponseHeaders(200,body.length);
                    try (var out=exchange.getResponseBody()) { out.write(body); }
                    LOG.info("request=http-7 method=GET path=/price status=200 total=30");
                });
                server.start();
                try {
                    var req=HttpRequest.newBuilder(URI.create("http://127.0.0.1:"+server.getAddress().getPort()+"/price")).timeout(Duration.ofSeconds(5)).GET().build();
                    try(var client=HttpClient.newHttpClient()) {
                        var response=client.send(req,HttpResponse.BodyHandlers.ofString());
                        assertEquals(200,response.statusCode());assertEquals("30",response.body());
                        assertEquals("http-7",response.headers().firstValue("X-Request-Id").orElseThrow());
                    }
                } finally { server.stop(0); }
            }));
            case "database" -> Stream.of(DynamicTest.dynamicTest("save distinct users", () -> {
                try(var c=DriverManager.getConnection("jdbc:h2:mem:routine", "sa", "")) {
                    try(var s=c.createStatement()) { s.execute("CREATE TABLE users(id INT PRIMARY KEY, email VARCHAR(100) UNIQUE)"); }
                    try(var s=c.prepareStatement("INSERT INTO users VALUES (?,?)")) {
                        for(int id=1;id<=2;id++) { s.setInt(1,id);s.setString(2,app.email(id));assertEquals(1,s.executeUpdate()); }
                    }
                    try(var s=c.createStatement();var r=s.executeQuery("SELECT COUNT(DISTINCT email) FROM users")) {r.next();assertEquals(2,r.getInt(1));}
                    LOG.info("request=db-7 operation=insert table=users rows=2 status=committed");
                }
            }));
            case "container" -> Stream.of(DynamicTest.dynamicTest("worker readiness", () -> {
                try(var box=new GenericContainer<>("alpine:3.22.1")
                    .withCommand("sh","-c","echo 'worker ready'; echo 'WARN cache stale request=worker-7 age=61s threshold=60s' >&2; sleep 45")
                    .withLogConsumer(frame -> FailureCasesTest.streamLog(frame,"routine-worker"))
                    .waitingFor(Wait.forLogMessage(app.readiness(),1)).withStartupTimeout(Duration.ofSeconds(8))) {
                    try {box.start();assertTrue(box.isRunning());LOG.info("request=worker-7 readiness=ok");}
                    finally {FailureCasesTest.containerLogs(box,"routine-worker");}
                }
            }));
            case "mixed" -> Stream.concat(
                java.util.stream.IntStream.rangeClosed(1,12).mapToObj(id -> DynamicTest.dynamicTest("user record "+id, () -> {
                    assertEquals("user"+id+"@example.test",app.email(id));
                    LOG.info("request=user-{} validation=ok",id);
                    if(id==6)routine();
                })), Stream.of(DynamicTest.dynamicTest("quantity pricing", () -> assertEquals(30,app.total(10,3),"quantity price"))));
            default -> throw new IllegalArgumentException("unknown scenario");
        };
    }
}
