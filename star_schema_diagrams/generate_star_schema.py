#!/usr/bin/env python3
"""
Star Schema Diagram Generator for Ad Campaign Analytics Portfolio
Generates a professional star schema visualization without requiring database connections.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
import os

def create_star_schema_diagram():
    """Create a professional star schema diagram for the Ad Campaign Analytics portfolio."""
    
    # Set up the figure with a professional style
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define colors
    fact_color = '#FF6B6B'  # Red for fact table
    dim_color = '#4ECDC4'   # Teal for dimension tables
    text_color = '#2C3E50'  # Dark blue for text
    line_color = '#34495E'  # Dark gray for lines
    
    # Fact Table (Center)
    fact_box = FancyBboxPatch((4.5, 4.5), 1, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor=fact_color, 
                              edgecolor='black', 
                              linewidth=2)
    ax.add_patch(fact_box)
    
    # Add fact table text
    ax.text(5, 5, 'FACT_CAMPAIGN\nPERFORMANCE', 
            ha='center', va='center', fontsize=10, fontweight='bold', 
            color='white', linespacing=1.2)
    
    # Dimension Tables (Surrounding the fact table)
    dim_tables = [
        # (x, y, width, height, name, description)
        (1, 7, 1.5, 0.8, 'DIM_CAMPAIGNS', 'Campaign Details'),
        (7, 7, 1.5, 0.8, 'DIM_PLATFORMS', 'Platform Info'),
        (1, 2, 1.5, 0.8, 'DIM_GEOGRAPHY', 'Geographic Data'),
        (7, 2, 1.5, 0.8, 'DIM_DEVICES', 'Device Info'),
        (4.5, 7.5, 1.5, 0.8, 'DIM_TIME', 'Time Dimensions'),
        (4.5, 1.5, 1.5, 0.8, 'DIM_AD_FORMATS', 'Ad Format Data')
    ]
    
    # Draw dimension tables
    for x, y, w, h, name, desc in dim_tables:
        dim_box = FancyBboxPatch((x, y), w, h, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=dim_color, 
                                 edgecolor='black', 
                                 linewidth=1.5)
        ax.add_patch(dim_box)
        
        # Add dimension table text
        ax.text(x + w/2, y + h/2 + 0.1, name, 
                ha='center', va='center', fontsize=9, fontweight='bold', 
                color='white')
        ax.text(x + w/2, y + h/2 - 0.1, desc, 
                ha='center', va='center', fontsize=7, color='white')
    
    # Draw connection lines from fact table to dimensions
    for x, y, w, h, name, desc in dim_tables:
        # Calculate connection points
        if y > 5:  # Top tables
            start_x, start_y = 5, 4.5
            end_x, end_y = x + w/2, y + h
        elif y < 5:  # Bottom tables
            start_x, start_y = 5, 4.5
            end_x, end_y = x + w/2, y + h
        else:  # Side tables
            if x < 5:  # Left tables
                start_x, start_y = 4.5, 5
                end_x, end_y = x + w, y + h/2
            else:  # Right tables
                start_x, start_y = 5.5, 5
                end_x, end_y = x, y + h/2
        
        # Draw connection line
        line = ConnectionPatch((start_x, start_y), (end_x, end_y), 
                              "data", "data", 
                              arrowstyle="->", 
                              shrinkA=5, shrinkB=5,
                              mutation_scale=20, 
                              fc=line_color, 
                              linewidth=2)
        ax.add_patch(line)
    
    # Add title and subtitle
    ax.text(5, 9.5, 'Ad Campaign Analytics - Star Schema', 
            ha='center', va='center', fontsize=20, fontweight='bold', 
            color=text_color)
    
    ax.text(5, 9, 'Data Model Architecture for Portfolio Showcase', 
            ha='center', va='center', fontsize=14, color=text_color)
    
    # Add legend
    legend_elements = [
        patches.Patch(color=fact_color, label='Fact Table (Measures)'),
        patches.Patch(color=dim_color, label='Dimension Tables (Attributes)')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', 
              bbox_to_anchor=(0.98, 0.98), fontsize=12)
    
    # Add key metrics info
    metrics_text = """
Key Metrics in Fact Table:
• Spend (decimal)
• Impressions (bigint)
• Clicks (bigint)
• Conversions (bigint)
• Conversion Value (decimal)
    """
    
    ax.text(0.5, 0.5, metrics_text, 
            ha='left', va='top', fontsize=10, 
            color=text_color, 
            bbox=dict(boxstyle="round,pad=0.5", 
                     facecolor='lightgray', 
                     alpha=0.8))
    
    # Add design benefits
    benefits_text = """
Star Schema Benefits:
• Fast query performance
• Easy to understand
• Flexible analysis
• Scalable design
    """
    
    ax.text(8.5, 0.5, benefits_text, 
            ha='left', va='top', fontsize=10, 
            color=text_color, 
            bbox=dict(boxstyle="round,pad=0.5", 
                     facecolor='lightblue', 
                     alpha=0.8))
    
    plt.tight_layout()
    return fig

def create_detailed_schema_diagram():
    """Create a more detailed schema diagram showing field relationships."""
    
    fig, ax = plt.subplots(1, 1, figsize=(20, 16))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 20)
    ax.axis('off')
    
    # Colors
    fact_color = '#FF6B6B'
    dim_color = '#4ECDC4'
    text_color = '#2C3E50'
    
    # Fact Table (Center)
    fact_box = FancyBboxPatch((9, 9), 2, 2, 
                              boxstyle="round,pad=0.1", 
                              facecolor=fact_color, 
                              edgecolor='black', 
                              linewidth=2)
    ax.add_patch(fact_box)
    
    # Fact table fields
    fact_fields = [
        'campaign_performance_id (PK)',
        'campaign_id (FK)',
        'platform_id (FK)',
        'geo_id (FK)',
        'device_id (FK)',
        'date_id (FK)',
        'ad_format_id (FK)',
        'spend (decimal)',
        'impressions (bigint)',
        'clicks (bigint)',
        'conversions (bigint)',
        'conversion_value (decimal)'
    ]
    
    ax.text(10, 10, 'FACT_CAMPAIGN_PERFORMANCE', 
            ha='center', va='center', fontsize=12, fontweight='bold', 
            color='white')
    
    # Draw dimension tables with fields
    dim_configs = [
        # (x, y, name, fields)
        (1, 15, 'DIM_CAMPAIGNS', [
            'campaign_id (PK)',
            'campaign_name',
            'campaign_type',
            'campaign_status',
            'campaign_objective',
            'start_date',
            'end_date',
            'budget'
        ]),
        (15, 15, 'DIM_PLATFORMS', [
            'platform_id (PK)',
            'platform_name',
            'platform_type',
            'platform_category',
            'is_active'
        ]),
        (1, 5, 'DIM_GEOGRAPHY', [
            'geo_id (PK)',
            'country_name',
            'country_code',
            'region_name',
            'city_name',
            'timezone',
            'currency'
        ]),
        (15, 5, 'DIM_DEVICES', [
            'device_id (PK)',
            'device_type',
            'device_category',
            'device_platform',
            'screen_resolution'
        ]),
        (9, 17, 'DIM_TIME', [
            'date_id (PK)',
            'full_date',
            'year',
            'quarter',
            'month',
            'week_of_year',
            'day_of_week'
        ]),
        (9, 1, 'DIM_AD_FORMATS', [
            'ad_format_id (PK)',
            'format_name',
            'format_type',
            'format_category',
            'dimensions',
            'is_video'
        ])
    ]
    
    # Draw dimension tables
    for x, y, name, fields in dim_configs:
        # Calculate box size based on number of fields
        height = max(1, len(fields) * 0.3)
        width = 2.5
        
        dim_box = FancyBboxPatch((x, y), width, height, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=dim_color, 
                                 edgecolor='black', 
                                 linewidth=1.5)
        ax.add_patch(dim_box)
        
        # Add table name
        ax.text(x + width/2, y + height - 0.1, name, 
                ha='center', va='center', fontsize=10, fontweight='bold', 
                color='white')
        
        # Add fields
        for i, field in enumerate(fields):
            field_y = y + height - 0.3 - (i * 0.25)
            if field_y > y:  # Only show if field fits in box
                ax.text(x + 0.1, field_y, field, 
                        ha='left', va='center', fontsize=7, color='white')
    
    # Draw connection lines
    for x, y, name, fields in dim_configs:
        # Calculate connection points
        if y > 10:  # Top tables
            start_x, start_y = 10, 9
            end_x, end_y = x + 1.25, y + height
        elif y < 10:  # Bottom tables
            start_x, start_y = 10, 9
            end_x, end_y = x + 1.25, y + height
        else:  # Side tables
            if x < 10:  # Left tables
                start_x, start_y = 9, 10
                end_x, end_y = x + width, y + height/2
            else:  # Right tables
                start_x, start_y = 11, 10
                end_x, end_y = x, y + height/2
        
        # Draw connection line
        line = ConnectionPatch((start_x, start_y), (end_x, end_y), 
                              "data", "data", 
                              arrowstyle="->", 
                              shrinkA=5, shrinkB=5,
                              mutation_scale=20, 
                              fc='#34495E', 
                              linewidth=2)
        ax.add_patch(line)
    
    # Add title
    ax.text(10, 19.5, 'Ad Campaign Analytics - Detailed Star Schema', 
            ha='center', va='center', fontsize=24, fontweight='bold', 
            color=text_color)
    
    ax.text(10, 19, 'Complete Data Model with Field Details', 
            ha='center', va='center', fontsize=16, color=text_color)
    
    # Add legend
    legend_elements = [
        patches.Patch(color=fact_color, label='Fact Table (Measures & Foreign Keys)'),
        patches.Patch(color=dim_color, label='Dimension Tables (Attributes & Primary Keys)')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', 
              bbox_to_anchor=(0.98, 0.98), fontsize=14)
    
    plt.tight_layout()
    return fig

def main():
    """Generate and save both star schema diagrams."""
    
    # Get current working directory
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("🌟 Generating Star Schema Diagrams for Ad Campaign Analytics Portfolio...")
    print(f"📁 Current working directory: {current_dir}")
    print(f"📁 Script location: {script_dir}")
    
    # Generate simple star schema
    print("📊 Creating simple star schema diagram...")
    fig1 = create_star_schema_diagram()
    fig1.savefig('star_schema_simple.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: star_schema_simple.png")
    
    # Generate detailed schema
    print("📊 Creating detailed schema diagram...")
    fig2 = create_detailed_schema_diagram()
    fig2.savefig('star_schema_detailed.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: star_schema_detailed.png")
    
    print("\n🎉 Star Schema Diagrams Generated Successfully!")
    print("📁 Files created:")
    print("   • star_schema_simple.png - Overview diagram")
    print("   • star_schema_detailed.png - Detailed field diagram")
    print(f"📁 Location: {os.path.abspath('.')}")
    print("\n💡 Use these diagrams in your portfolio to showcase:")
    print("   • Data modeling skills")
    print("   • Architecture design knowledge")
    print("   • Business understanding")
    print("   • Technical expertise")
    
    # Show the diagrams
    plt.show()

if __name__ == "__main__":
    main()
