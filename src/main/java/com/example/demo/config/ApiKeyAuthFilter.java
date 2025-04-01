package com.example.demo.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;


public class ApiKeyAuthFilter extends OncePerRequestFilter {

    private final String headerName;
    private final String apiKey;

    public ApiKeyAuthFilter(String headerName, String apiKey) {
        this.headerName = headerName;
        this.apiKey = apiKey;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws ServletException, IOException {
        String requestApiKey = request.getHeader(headerName);

        if (request.getRequestURI().startsWith("/api/ai/")) {
            if (requestApiKey == null || !requestApiKey.equals(apiKey)) {
                response.sendError(HttpStatus.UNAUTHORIZED.value(), "Invalid API Key");
                return;
            }
            Authentication auth = new UsernamePasswordAuthenticationToken(
                    "ai-service", null, List.of(new SimpleGrantedAuthority("ROLE_AI_SERVICE"))
            );
            SecurityContextHolder.getContext().setAuthentication(auth);
        }
        filterChain.doFilter(request, response);
    }
}
