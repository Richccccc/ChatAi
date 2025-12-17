package com.over;

import org.junit.jupiter.api.Test;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

public class DatabaseImportTest {

    @Test
    public void importJobPostings() {
        String url = "jdbc:mysql://gateway01.eu-central-1.prod.aws.tidbcloud.com:4000/over?useSSL=true&serverTimezone=Asia/Shanghai&characterEncoding=UTF-8&useUnicode=true&allowPublicKeyRetrieval=true";
        String username = "uCdsi6MEYsN9k31.root";
        String password = "srcN4mkWxbQUHWyR";
        String filePath = "d:\\project\\backend\\sql\\job_postings.sql";

        try (Connection conn = DriverManager.getConnection(url, username, password);
             Statement stmt = conn.createStatement();
             BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(filePath), StandardCharsets.UTF_8))) {

            System.out.println("Connected to database successfully.");

            String line;
            StringBuilder sqlBuilder = new StringBuilder();
            long count = 0;
            boolean inBlockComment = false;

            conn.setAutoCommit(false); 

            while ((line = br.readLine()) != null) {
                line = line.trim();
                
                if (line.startsWith("/*")) {
                    inBlockComment = true;
                }
                
                if (inBlockComment) {
                    if (line.endsWith("*/")) {
                        inBlockComment = false;
                    }
                    continue;
                }

                if (line.isEmpty() || line.startsWith("--")) {
                    continue;
                }

                sqlBuilder.append(line);
                if (line.endsWith(";")) {
                    String sql = sqlBuilder.toString();
                    try {
                        stmt.execute(sql);
                        count++;
                        if (count % 100 == 0) {
                            System.out.println("Executed " + count + " statements...");
                            conn.commit();
                        }
                    } catch (Exception e) {
                        System.err.println("Failed to execute: " + sql.substring(0, Math.min(sql.length(), 100)) + "...");
                        // Don't fail the whole process, just log
                    }
                    sqlBuilder.setLength(0);
                } else {
                    sqlBuilder.append(" ");
                }
            }
            conn.commit();
            System.out.println("Import completed. Total statements executed: " + count);

        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException(e);
        }
    }
}
