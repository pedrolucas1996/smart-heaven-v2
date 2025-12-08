"""CLI script for database cleanup operations."""
import asyncio
import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infra.db import init_db, database
from src.services.cleanup_service import CleanupService


async def cleanup_logs(days: int = None, limit: int = None):
    """Run log cleanup."""
    await init_db()
    
    async with database.session() as db:
        service = CleanupService(db)
        
        print("📊 Current log statistics:")
        stats = await service.get_logs_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
        
        if days:
            print(f"🧹 Cleaning logs older than {days} days...")
            deleted = await service.cleanup_old_logs(days)
            print(f"✅ Deleted {deleted} old log records")
        
        if limit:
            print(f"🧹 Keeping only {limit} most recent logs...")
            deleted = await service.cleanup_logs_by_limit(limit)
            print(f"✅ Deleted {deleted} log records")
        
        print("\n📊 Updated log statistics:")
        stats = await service.get_logs_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")


async def cleanup_lights():
    """Run lights cleanup (remove duplicates)."""
    await init_db()
    
    async with database.session() as db:
        service = CleanupService(db)
        
        print("📊 Current lights statistics:")
        stats = await service.get_lights_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
        
        if stats["duplicates_exist"]:
            print("🧹 Cleaning duplicate light records...")
            deleted = await service.cleanup_duplicate_lights()
            print(f"✅ Deleted {deleted} duplicate records")
            
            print("\n📊 Updated lights statistics:")
            stats = await service.get_lights_statistics()
            for key, value in stats.items():
                print(f"  {key}: {value}")
        else:
            print("✨ No duplicates found!")


async def show_statistics():
    """Show database statistics."""
    await init_db()
    
    async with database.session() as db:
        service = CleanupService(db)
        
        print("=" * 50)
        print("📊 DATABASE STATISTICS")
        print("=" * 50)
        
        print("\n🗄️ LOGS TABLE:")
        log_stats = await service.get_logs_statistics()
        for key, value in log_stats.items():
            print(f"  {key}: {value}")
        
        print("\n💡 LIGHTS TABLE:")
        light_stats = await service.get_lights_statistics()
        for key, value in light_stats.items():
            print(f"  {key}: {value}")
        
        print("\n" + "=" * 50)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Smart Heaven Database Cleanup Tool"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Logs cleanup command
    logs_parser = subparsers.add_parser("logs", help="Clean old log records")
    logs_parser.add_argument(
        "--days",
        type=int,
        help="Delete logs older than N days (e.g., --days 7)"
    )
    logs_parser.add_argument(
        "--limit",
        type=int,
        help="Keep only N most recent logs (e.g., --limit 1000)"
    )
    
    # Lights cleanup command
    subparsers.add_parser("lights", help="Clean duplicate light records")
    
    # Statistics command
    subparsers.add_parser("stats", help="Show database statistics")
    
    args = parser.parse_args()
    
    if args.command == "logs":
        if not args.days and not args.limit:
            print("❌ Error: Please specify --days or --limit")
            sys.exit(1)
        asyncio.run(cleanup_logs(args.days, args.limit))
    
    elif args.command == "lights":
        asyncio.run(cleanup_lights())
    
    elif args.command == "stats":
        asyncio.run(show_statistics())
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
