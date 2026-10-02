package com.ai.token.experiment;

public class RoutineService {
    public int total(int price, int quantity) { return price * quantity; }
    public String email(int id) { return "user" + id + "@example.test"; }
    public String readiness() { return ".*worker ready.*\\n"; }
}
