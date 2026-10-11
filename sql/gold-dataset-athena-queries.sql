# clv pipeline total revenue

SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(order_revenue), 2) AS total_revenue,
    COUNT(DISTINCT restaurant_id) AS restaurants
FROM clv_analytics.order_sales;

# clv pipeline metrics

SELECT
    (SELECT COUNT(*)
     FROM clv_analytics.customer_metrics) AS total_customers,

    (SELECT ROUND(SUM(historical_clv), 2)
     FROM clv_analytics.customer_metrics) AS identified_customer_revenue,

    (SELECT ROUND(SUM(total_revenue), 2)
     FROM clv_analytics.restaurant_performance) AS restaurant_revenue;