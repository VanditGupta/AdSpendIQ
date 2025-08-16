#!/usr/bin/env python3
"""
Data Retention Manager for Ad Campaign Spend Tracker

This script handles data retention policies to prevent infinite data growth.
It cleans up both local files and Snowflake database, keeping only the last 90 days.

Author: Vandit Gupta
Date: August 15, 2025
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import shutil

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scripts.load_backfill_to_snowflake import create_snowflake_connection

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Retention configuration
RETENTION_DAYS = 90  # Keep last 90 days of data
ARCHIVE_ENABLED = True  # Whether to archive old data before deletion

class DataRetentionManager:
    """
    Manages data retention for both local files and Snowflake database.
    """
    
    def __init__(self, retention_days=90, archive_enabled=True):
        self.retention_days = retention_days
        self.archive_enabled = archive_enabled
        self.cutoff_date = datetime.now().date() - timedelta(days=retention_days)
        
    def cleanup_local_files(self):
        """
        Clean up old local data files, keeping only last N days.
        Archives old files before deletion.
        """
        try:
            logger.info(f"🧹 Starting local file cleanup (keeping last {self.retention_days} days)")
            logger.info(f"📅 Cutoff date: {self.cutoff_date}")
            
            # Clean daily data files
            daily_data_path = Path("data/raw/daily")
            if daily_data_path.exists():
                self._cleanup_daily_files(daily_data_path)
            
            # Clean historical data if it's too old
            historical_data_path = Path("data/raw/historical")
            if historical_data_path.exists():
                self._cleanup_historical_files(historical_data_path)
            
            logger.info("✅ Local file cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Local file cleanup failed: {e}")
            raise
    
    def _cleanup_daily_files(self, daily_path: Path):
        """Clean up old daily data files with archiving."""
        logger.info(f"📁 Cleaning daily files in: {daily_path}")
        
        files_removed = 0
        files_archived = 0
        total_size_removed = 0
        
        for year_dir in daily_path.iterdir():
            if not year_dir.is_dir():
                continue
                
            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue
                    
                for file_path in month_dir.glob("ads_*.csv"):
                    try:
                        # Extract date from filename (ads_YYYY-MM-DD.csv)
                        date_str = file_path.stem.split('_')[1]
                        file_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        
                        if file_date < self.cutoff_date:
                            # Archive if enabled
                            if self.archive_enabled:
                                archive_path = self._archive_file(file_path)
                                logger.info(f"📦 Archived: {file_path.name} -> {archive_path}")
                                files_archived += 1
                            
                            # Remove file
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            
                            files_removed += 1
                            total_size_removed += file_size
                            
                            logger.info(f"🗑️ Removed old file: {file_path.name} ({file_date})")
                            
                    except (ValueError, IndexError) as e:
                        logger.warning(f"⚠️ Could not parse date from filename: {file_path.name}")
                        continue
        
        # Remove empty directories
        self._remove_empty_directories(daily_path)
        
        logger.info(f"📊 Daily files cleanup: {files_removed} files removed, {files_archived} archived, {total_size_removed / 1024 / 1024:.2f} MB freed")
    
    def _cleanup_historical_files(self, historical_path: Path):
        """Clean up historical data files if they're too old."""
        logger.info(f"📁 Checking historical files in: {historical_path}")
        
        files_removed = 0
        files_archived = 0
        
        for file_path in historical_path.glob("*.csv"):
            try:
                # Check file modification time
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime).date()
                
                if file_mtime < self.cutoff_date:
                    # Archive if enabled
                    if self.archive_enabled:
                        archive_path = self._archive_file(file_path)
                        logger.info(f"📦 Archived: {file_path.name} -> {archive_path}")
                        files_archived += 1
                    
                    # Remove file
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    
                    files_removed += 1
                    logger.info(f"🗑️ Removed old historical file: {file_path.name} (modified: {file_mtime})")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error processing historical file {file_path.name}: {e}")
                continue
        
        if files_removed > 0 or files_archived > 0:
            logger.info(f"📊 Historical files cleanup: {files_removed} files removed, {files_archived} archived")
    
    def _archive_file(self, file_path: Path) -> Path:
        """Archive a file to the archive directory with timestamp."""
        # Create archive directory structure
        archive_dir = Path("data/archive") / file_path.parent.name
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped archive filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_filename = f"{file_path.stem}_{timestamp}.csv"
        archive_path = archive_dir / archive_filename
        
        # Copy file to archive
        shutil.copy2(file_path, archive_path)
        
        return archive_path
    
    def _remove_empty_directories(self, start_path: Path):
        """Remove empty directories recursively."""
        for path in sorted(start_path.rglob('*'), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                try:
                    path.rmdir()
                    logger.debug(f"🗑️ Removed empty directory: {path}")
                except OSError:
                    pass  # Directory not empty or permission denied
    
    def cleanup_snowflake_data(self):
        """
        Clean up old data in Snowflake, keeping only last N days.
        Archives old data before deletion to prevent data loss.
        """
        try:
            logger.info(f"🗄️ Starting Snowflake data cleanup (keeping last {self.retention_days} days)")
            logger.info(f"📅 Cutoff date: {self.cutoff_date}")
            
            conn = create_snowflake_connection()
            cursor = conn.cursor()
            
            try:
                # Get count of rows to be deleted
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM raw.ad_data 
                    WHERE date < %s
                """, (self.cutoff_date,))
                
                rows_to_delete = cursor.fetchone()[0]
                
                if rows_to_delete == 0:
                    logger.info("✅ No old data to clean up in Snowflake")
                    return 0
                
                logger.info(f"📊 Found {rows_to_delete:,} rows older than {self.cutoff_date}")
                
                # Archive old data if enabled
                if self.archive_enabled:
                    archived_rows = self._archive_snowflake_data(cursor, self.cutoff_date)
                    logger.info(f"📦 Successfully archived {archived_rows:,} rows")
                
                # Delete old data
                cursor.execute("""
                    DELETE FROM raw.ad_data 
                    WHERE date < %s
                """, (self.cutoff_date,))
                
                deleted_rows = cursor.rowcount
                logger.info(f"🗑️ Deleted {deleted_rows:,} old rows from Snowflake")
                
                # Get remaining row count
                cursor.execute("SELECT COUNT(*) FROM raw.ad_data")
                remaining_rows = cursor.fetchone()[0]
                logger.info(f"📊 Remaining rows in Snowflake: {remaining_rows:,}")
                
                return deleted_rows
                
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            logger.error(f"❌ Snowflake cleanup failed: {e}")
            raise
    
    def _archive_snowflake_data(self, cursor, cutoff_date):
        """Archive old Snowflake data before deletion."""
        try:
            logger.info("📦 Archiving old Snowflake data...")
            
            # Create archive table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raw.ad_data_archive (
                    campaign_id VARCHAR(255),
                    platform VARCHAR(50),
                    date DATE,
                    geo VARCHAR(50),
                    device VARCHAR(50),
                    campaign_type VARCHAR(100),
                    ad_format VARCHAR(100),
                    impressions INTEGER,
                    clicks INTEGER,
                    spend DECIMAL(10,2),
                    conversions INTEGER
                )
            """)
            
            # Insert old data into archive
            cursor.execute("""
                INSERT INTO raw.ad_data_archive 
                SELECT * FROM raw.ad_data 
                WHERE date < %s
            """, (cutoff_date,))
            
            archived_rows = cursor.rowcount
            logger.info(f"📦 Archived {archived_rows:,} rows to raw.ad_data_archive")
            
            return archived_rows
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to archive Snowflake data: {e}")
            # Continue with deletion even if archiving fails
            return 0
    
    def run_full_cleanup(self):
        """
        Run complete data retention cleanup for both local files and Snowflake.
        """
        try:
            logger.info("🚀 Starting comprehensive data retention cleanup")
            
            # Clean local files
            self.cleanup_local_files()
            
            # Clean Snowflake data
            deleted_rows = self.cleanup_snowflake_data()
            
            logger.info("✅ Data retention cleanup completed successfully")
            return deleted_rows
            
        except Exception as e:
            logger.error(f"❌ Data retention cleanup failed: {e}")
            raise
    
    def get_cleanup_summary(self):
        """
        Get a summary of what would be cleaned up without actually doing it.
        """
        try:
            summary = {
                'retention_days': self.retention_days,
                'cutoff_date': self.cutoff_date,
                'local_files': self._count_local_files_to_cleanup(),
                'snowflake_rows': self._count_snowflake_rows_to_cleanup()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get cleanup summary: {e}")
            raise
    
    def _count_local_files_to_cleanup(self):
        """Count local files that would be cleaned up."""
        count = 0
        daily_path = Path("data/raw/daily")
        
        if daily_path.exists():
            for file_path in daily_path.rglob("ads_*.csv"):
                try:
                    date_str = file_path.stem.split('_')[1]
                    file_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    if file_date < self.cutoff_date:
                        count += 1
                except (ValueError, IndexError):
                    continue
        
        return count
    
    def _count_snowflake_rows_to_cleanup(self):
        """Count Snowflake rows that would be cleaned up."""
        try:
            conn = create_snowflake_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM raw.ad_data 
                WHERE date < %s
            """, (self.cutoff_date,))
            
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            return count
            
        except Exception:
            return 0

def main():
    """Main function for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Retention Manager')
    parser.add_argument('--retention-days', type=int, default=90, 
                       help='Number of days to retain (default: 90)')
    parser.add_argument('--no-archive', action='store_true',
                       help='Disable archiving before deletion')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be cleaned up without doing it')
    parser.add_argument('--cleanup', action='store_true',
                       help='Run the actual cleanup')
    
    args = parser.parse_args()
    
    # Create retention manager
    manager = DataRetentionManager(
        retention_days=args.retention_days,
        archive_enabled=not args.no_archive
    )
    
    try:
        if args.dry_run:
            # Show summary
            summary = manager.get_cleanup_summary()
            print(f"\n📊 Data Retention Summary:")
            print(f"   Retention period: {summary['retention_days']} days")
            print(f"   Cutoff date: {summary['cutoff_date']}")
            print(f"   Local files to remove: {summary['local_files']}")
            print(f"   Snowflake rows to remove: {summary['snowflake_rows']:,}")
            print(f"   Archive enabled: {not args.no_archive}")
            
        elif args.cleanup:
            # Run actual cleanup
            deleted_rows = manager.run_full_cleanup()
            print(f"✅ Cleanup completed! Removed {deleted_rows:,} old rows from Snowflake")
            
        else:
            # Show help
            parser.print_help()
            print(f"\n💡 Examples:")
            print(f"   # Show what would be cleaned up:")
            print(f"   python scripts/data_retention_manager.py --dry-run")
            print(f"   # Run actual cleanup:")
            print(f"   python scripts/data_retention_manager.py --cleanup")
            print(f"   # Custom retention period:")
            print(f"   python scripts/data_retention_manager.py --retention-days 30 --cleanup")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
