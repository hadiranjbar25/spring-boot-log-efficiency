from pathlib import Path
p=Path('pom.xml'); s=p.read_text()
s=s.replace('\n</project>', '''
  <profiles>
    <profile>
      <id>investigation</id>
      <dependencies>
        <dependency><groupId>org.springframework</groupId><artifactId>spring-webmvc</artifactId><scope>test</scope></dependency>
        <dependency><groupId>jakarta.servlet</groupId><artifactId>jakarta.servlet-api</artifactId><scope>test</scope></dependency>
        <dependency><groupId>com.h2database</groupId><artifactId>h2</artifactId><scope>test</scope></dependency>
        <dependency><groupId>org.testcontainers</groupId><artifactId>testcontainers-postgresql</artifactId><scope>test</scope></dependency>
        <dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><scope>test</scope></dependency>
      </dependencies>
      <build><plugins>
        <plugin><groupId>org.codehaus.mojo</groupId><artifactId>build-helper-maven-plugin</artifactId><version>3.6.1</version>
          <executions>
            <execution><id>experiment-java</id><phase>generate-test-sources</phase><goals><goal>add-test-source</goal></goals><configuration><sources><source>investigation/src/test/java</source></sources></configuration></execution>
            <execution><id>experiment-resources</id><phase>generate-test-resources</phase><goals><goal>add-test-resource</goal></goals><configuration><resources><resource><directory>investigation/src/test/resources</directory></resource></resources></configuration></execution>
          </executions>
        </plugin>
      </plugins></build>
    </profile>
    <profile><id>agent-reports</id><build><plugins>
      <plugin><groupId>org.apache.maven.plugins</groupId><artifactId>maven-surefire-plugin</artifactId><configuration><trimStackTrace>true</trimStackTrace></configuration></plugin>
    </plugins></build></profile>
  </profiles>
</project>''')
p.write_text(s)
prefix='%d{HH:mm:ss.SSS} %level [%thread] %logger{36}: %msg%n${LOG_EXCEPTION_CONVERSION_WORD:-%wEx}'
# Remove only complete JUnit / reflective invocation frame lines, never exception headers.
exception="%replace(%wEx){'(?m)^[ \\t]+at (?:org\\.junit\\.|org\\.apache\\.maven\\.surefire\\.|java\\.lang\\.reflect\\.|jdk\\.internal\\.reflect\\.)[^\\r\\n]*[\\r\\n]+',''}"
def yaml_value(x): return '"'+x.replace('\\','\\\\').replace('"','\\"')+'"'
Path('src/main/resources/application-agent.yml').write_text('# Opt-in local console formatting. No log levels or application behavior change.\nlogging:\n  pattern:\n    console: '+yaml_value(prefix)+'\n    exception-conversion-word: '+yaml_value(exception)+'\n')
Path('investigation/src/test/resources/application-p1.yml').write_text('logging:\n  pattern:\n    console: '+yaml_value(prefix)+'\n')
Path('investigation/src/test/resources/application-p2.yml').write_text('logging:\n  pattern:\n    exception-conversion-word: '+yaml_value(exception)+'\n')
