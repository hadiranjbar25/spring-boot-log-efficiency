package com.ai.token.experiment;

import java.io.*;
import java.net.URI;
import java.net.http.*;
import java.sql.*;
import java.util.concurrent.*;
import org.slf4j.*;
import org.springframework.context.annotation.*;
import org.springframework.web.bind.annotation.*;

/** Deliberately defective fixture. Never on the normal application classpath. */
public class Defects {
    private static final Logger LOG = LoggerFactory.getLogger(Defects.class);
    public int total(int price, int quantity) { return price + quantity; }
    public int parsePort(String port) { return Integer.parseInt(port); }
    public int connect() {
        try { return parsePort("eighty"); }
        catch (NumberFormatException e) {
            var cause = new IOException("invalid upstream port", e);
            var failure = new IllegalStateException("cannot initialize client", cause);
            failure.addSuppressed(new IOException("cleanup socket failed"));
            throw failure;
        }
    }
    @RestController
    public static class Orders {
        @GetMapping("/orders") public String orders(@RequestParam("count") int count) { return "count=" + count; }
    }
    public String ordersUrl() { return "/orders?count=two"; }
    @Configuration(proxyBeanMethods=false)
    public static class BrokenStartup {
        @Bean String port() { return "port=" + Integer.parseInt("eighty"); }
    }
    public Connection database(String url, String user, String password) throws SQLException {
        var c = DriverManager.getConnection(url, user, password);
        try (var s = c.createStatement()) { s.execute("CREATE TABLE users(id INT PRIMARY KEY, email VARCHAR(100), CONSTRAINT uq_email UNIQUE(email))"); }
        return c;
    }
    public void save(Connection c) throws SQLException {
        try (var s = c.prepareStatement("INSERT INTO users VALUES (?, ?)")) {
            for (int id=1; id<=2; id++) { s.setInt(1,id); s.setString(2,"same@example.test"); s.executeUpdate(); }
        }
    }
    public boolean saveCaught(Connection c) {
        try { save(c); return true; }
        catch (SQLException e) {
            LOG.error("save users failed request=db-6", e);
            // P3: sole exception owner; keep the second event and its context.
            if (Boolean.getBoolean("experiment.deduplicate")) LOG.error("request=db-6 failed; exception logged by save users");
            else LOG.error("request=db-6 failed at service boundary", e);
            return false;
        }
    }
    public int call(URI base) {
        return org.springframework.web.client.RestClient.create().get().uri(base.resolve("/wrong")).retrieve().body(Integer.class);
    }
    public int async() throws Exception {
        try (var executor = Executors.newSingleThreadExecutor(r -> new Thread(r,"invoice-worker-7"))) {
            return executor.submit(() -> {
                org.slf4j.MDC.put("request", "invoice-42");
                try { return Integer.parseInt("ten"); }
                catch (RuntimeException e) { LOG.error("invoice-42 calculation failed", e); throw e; }
                finally { org.slf4j.MDC.clear(); }
            }).get(5, TimeUnit.SECONDS);
        }
    }
    public String readyPattern() { return ".*service ready.*\\n"; }
}
