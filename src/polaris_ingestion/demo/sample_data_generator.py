"""
Sample Data Generator

Utility for generating sample data in Polaris demo tables.
"""

import random
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from ..utils.config_manager import IngestionConfig


class SampleDataGenerator:
    """
    Generates realistic sample data for demo tables in Apache Polaris.
    
    This class creates sample datasets that demonstrate:
    - Realistic business data patterns
    - Proper data types and constraints
    - Relationships between tables
    - Time-series data for analytics
    """
    
    def __init__(self, config: IngestionConfig):
        """
        Initialize the sample data generator.
        
        Args:
            config: Complete ingestion configuration
        """
        self.config = config
        
        # Sample data templates
        self.regions = ['North', 'South', 'East', 'West', 'Central']
        self.customer_segments = ['Premium', 'Standard', 'Budget', 'Enterprise', 'Startup']
        self.product_categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']
        self.order_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        
        self.first_names = [
            'Alice', 'Bob', 'Charlie', 'Diana', 'Edward', 'Fiona', 'George', 'Helen',
            'Ivan', 'Julia', 'Kevin', 'Linda', 'Michael', 'Nancy', 'Oscar', 'Patricia',
            'Quinn', 'Rachel', 'Steven', 'Teresa'
        ]
        
        self.last_names = [
            'Anderson', 'Brown', 'Clark', 'Davis', 'Evans', 'Foster', 'Garcia', 'Harris',
            'Jackson', 'Johnson', 'King', 'Lee', 'Martinez', 'Nelson', 'Parker', 'Rodriguez',
            'Smith', 'Taylor', 'Wilson', 'Young'
        ]
        
        self.product_names = [
            'Laptop Pro', 'Wireless Headphones', 'Smart Watch', 'Tablet', 'Smartphone',
            'Running Shoes', 'Winter Jacket', 'Coffee Maker', 'Office Chair', 'Desk Lamp',
            'Programming Book', 'Cookbook', 'Novel', 'Art Supplies', 'Yoga Mat'
        ]
    
    def generate_customers(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Generate sample customer data.
        
        Args:
            count: Number of customers to generate
            
        Returns:
            List of customer records
        """
        customers = []
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2024, 1, 1)
        
        for i in range(1, count + 1):
            # Generate random registration date
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            registration_date = start_date + timedelta(days=random_days)
            
            customer = {
                'customer_id': i,
                'first_name': random.choice(self.first_names),
                'last_name': random.choice(self.last_names),
                'email': f'customer{i}@example.com',
                'registration_date': registration_date.strftime('%Y-%m-%d')
            }
            customers.append(customer)
        
        return customers
    
    def generate_products(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Generate sample product data.
        
        Args:
            count: Number of products to generate
            
        Returns:
            List of product records
        """
        products = []
        
        for i in range(1, count + 1):
            product = {
                'product_id': i,
                'name': f"{random.choice(self.product_names)} {i}",
                'category': random.choice(self.product_categories),
                'price': round(random.uniform(10.99, 999.99), 2),
                'stock_quantity': random.randint(0, 500)
            }
            products.append(product)
        
        return products
    
    def generate_orders(self, customer_count: int = 100, product_count: int = 50, 
                       order_count: int = 500) -> List[Dict[str, Any]]:
        """
        Generate sample order data.
        
        Args:
            customer_count: Number of customers (for FK references)
            product_count: Number of products (for FK references) 
            order_count: Number of orders to generate
            
        Returns:
            List of order records
        """
        orders = []
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        for i in range(1, order_count + 1):
            # Generate random order date
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            order_date = start_date + timedelta(days=random_days)
            
            order = {
                'order_id': i,
                'customer_id': random.randint(1, customer_count),
                'order_date': order_date.strftime('%Y-%m-%d'),
                'total_amount': round(random.uniform(15.99, 1599.99), 2),
                'status': random.choice(self.order_statuses)
            }
            orders.append(order)
        
        return orders
    
    def generate_monthly_sales(self, months: int = 24) -> List[Dict[str, Any]]:
        """
        Generate monthly sales aggregation data.
        
        Args:
            months: Number of months of data to generate
            
        Returns:
            List of monthly sales records
        """
        monthly_sales = []
        start_date = datetime(2023, 1, 1)
        
        for i in range(months):
            month_date = start_date + timedelta(days=30 * i)
            
            for region in self.regions:
                # Generate realistic sales data with some seasonality
                base_sales = random.uniform(50000, 200000)
                seasonal_factor = 1 + 0.3 * random.sin(2 * 3.14159 * i / 12)  # Annual cycle
                total_sales = base_sales * seasonal_factor
                
                monthly_sale = {
                    'month': month_date.strftime('%Y-%m-01'),
                    'region': region,
                    'total_sales': round(total_sales, 2),
                    'total_orders': random.randint(100, 1000),
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                monthly_sales.append(monthly_sale)
        
        return monthly_sales
    
    def generate_customer_segmentation(self, customer_count: int = 100) -> List[Dict[str, Any]]:
        """
        Generate customer segmentation analysis data.
        
        Args:
            customer_count: Number of customers to generate segments for
            
        Returns:
            List of customer segmentation records
        """
        segmentation = []
        
        for customer_id in range(1, customer_count + 1):
            segment = random.choice(self.customer_segments)
            
            # Generate LTV based on segment
            ltv_ranges = {
                'Premium': (5000, 15000),
                'Enterprise': (10000, 50000),
                'Standard': (1000, 5000),
                'Budget': (100, 1000),
                'Startup': (500, 3000)
            }
            
            ltv_min, ltv_max = ltv_ranges[segment]
            ltv = round(random.uniform(ltv_min, ltv_max), 2)
            
            segmentation_record = {
                'customer_id': customer_id,
                'segment': segment,
                'ltv': ltv,
                'segment_score': round(random.uniform(0.1, 1.0), 3),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            segmentation.append(segmentation_record)
        
        return segmentation
    
    def generate_all_sample_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate complete sample dataset for all demo tables.
        
        Returns:
            Dictionary containing all sample data organized by table
        """
        print("🎲 Generating Sample Data...")
        print("-" * 30)
        
        # Generate base data
        customers = self.generate_customers(100)
        products = self.generate_products(50)
        orders = self.generate_orders(100, 50, 500)
        monthly_sales = self.generate_monthly_sales(24)
        customer_segmentation = self.generate_customer_segmentation(100)
        
        sample_data = {
            'customers': customers,
            'products': products,
            'orders': orders,
            'monthly_sales': monthly_sales,
            'customer_segmentation': customer_segmentation
        }
        
        # Print summary
        print(f"📊 Generated Sample Data:")
        for table_name, data in sample_data.items():
            print(f"   • {table_name}: {len(data)} records")
        
        return sample_data
    
    def save_sample_data(self, sample_data: Dict[str, List[Dict[str, Any]]], 
                        output_dir: str = "data") -> bool:
        """
        Save sample data to JSON files.
        
        Args:
            sample_data: Generated sample data
            output_dir: Directory to save files to
            
        Returns:
            bool: True if save succeeded
        """
        try:
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            for table_name, data in sample_data.items():
                file_path = os.path.join(output_dir, f"{table_name}.json")
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                print(f"💾 Saved {table_name} data to {file_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving sample data: {e}")
            return False
    
    def print_sample_preview(self, sample_data: Dict[str, List[Dict[str, Any]]], 
                           preview_rows: int = 3) -> None:
        """
        Print a preview of the generated sample data.
        
        Args:
            sample_data: Generated sample data
            preview_rows: Number of rows to show per table
        """
        print(f"\n📋 Sample Data Preview (showing {preview_rows} rows per table):")
        print("=" * 60)
        
        for table_name, data in sample_data.items():
            print(f"\n🔹 {table_name.upper()}:")
            
            if not data:
                print("   (No data)")
                continue
            
            # Show column headers
            if data:
                headers = list(data[0].keys())
                print(f"   Columns: {', '.join(headers)}")
            
            # Show preview rows
            for i, row in enumerate(data[:preview_rows]):
                print(f"   Row {i+1}: {row}")
            
            if len(data) > preview_rows:
                print(f"   ... and {len(data) - preview_rows} more rows")
        
        print("=" * 60)