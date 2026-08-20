"""Seed script to create sample CMS data and initial settings."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.session import AsyncSessionLocal
from app.models.cms_page import CMSPage
from app.models.app_settings import AppSettings
from app.models.contact_information import ContactInformation


async def seed_cms_pages():
    """Seed sample CMS pages."""
    pages = [
        CMSPage(
            title="About GFRP",
            slug="about",
            description="<p>Glass Fiber Reinforced Polymer (GFRP) rebar is a revolutionary alternative to traditional steel reinforcement.</p>",
            display_order=1,
            is_active=True,
            meta_title="About GFRP - Shree Glass Fiber",
            meta_description="Learn about Glass Fiber Reinforced Polymer rebar technology",
        ),
        CMSPage(
            title="Applications",
            slug="application",
            description="<p>GFRP rebar is used in bridges, marine structures, tunnels, and corrosive environments.</p>",
            display_order=2,
            is_active=True,
            meta_title="GFRP Applications",
            meta_description="Discover the applications of GFRP rebar in construction",
        ),
        CMSPage(
            title="Benefits of GFRP Rebar",
            slug="benefits",
            description="<p>Non-corrosive, lightweight, high tensile strength, and electromagnetic transparency.</p>",
            display_order=3,
            is_active=True,
            meta_title="Benefits of GFRP Rebar",
            meta_description="Key benefits of using GFRP rebar over traditional steel",
        ),
        CMSPage(
            title="Technical Specification",
            slug="specification",
            description="<p>Detailed technical specifications for GFRP rebar products.</p>",
            display_order=4,
            is_active=True,
            meta_title="Technical Specifications",
            meta_description="GFRP rebar technical specifications and data sheets",
        ),
        CMSPage(
            title="Worldwide Standards & Certification",
            slug="standards",
            description="<p>GFRP rebar meets international standards including ASTM, ISO, and ACI guidelines.</p>",
            display_order=5,
            is_active=True,
            meta_title="Standards & Certification",
            meta_description="International standards and certifications for GFRP rebar",
        ),
        CMSPage(
            title="Download Brochure",
            slug="brochure",
            description="<p>Download our complete product brochure for detailed information.</p>",
            display_order=6,
            is_active=True,
            meta_title="Download Brochure",
            meta_description="Download GFRP rebar product brochure",
        ),
    ]
    return pages


async def seed_settings():
    """Seed default application settings."""
    settings_data = [
        AppSettings(key="youtube_url", value="", description="YouTube channel URL"),
        AppSettings(key="instagram_url", value="", description="Instagram profile URL"),
        AppSettings(key="facebook_url", value="", description="Facebook page URL"),
        AppSettings(key="company_name", value="Shree Glass Fiber", description="Company name"),
        AppSettings(key="company_logo", value="", description="Company logo URL"),
        AppSettings(key="brochure_pdf", value="", description="Brochure PDF URL"),
        AppSettings(key="support_email", value="support@shreeglass.com", description="Support email"),
        AppSettings(key="support_phone", value="", description="Support phone number"),
        AppSettings(key="privacy_policy_url", value="", description="Privacy policy URL"),
        AppSettings(key="terms_url", value="", description="Terms & conditions URL"),
        AppSettings(key="android_min_version", value="1.0.0", description="Minimum Android app version"),
        AppSettings(key="ios_min_version", value="1.0.0", description="Minimum iOS app version"),
        AppSettings(key="force_update", value="false", description="Force app update (true/false)"),
        AppSettings(key="maintenance_mode", value="false", description="Maintenance mode (true/false)"),
    ]
    return settings_data


async def seed_contact():
    """Seed default contact information."""
    return ContactInformation(
        office_name="Shree Glass Fiber Pvt. Ltd.",
        phone="+91-9876543210",
        email="info@shreeglass.com",
        website="https://shreeglass.com",
        address="Industrial Area, Gujarat, India",
        google_map_url="",
    )


async def run_seed():
    """Run all seed operations."""
    async with AsyncSessionLocal() as session:
        try:
            # Seed CMS pages
            pages = await seed_cms_pages()
            for page in pages:
                session.add(page)
            print(f"✓ Seeded {len(pages)} CMS pages")

            # Seed settings
            settings = await seed_settings()
            for setting in settings:
                session.add(setting)
            print(f"✓ Seeded {len(settings)} app settings")

            # Seed contact
            contact = await seed_contact()
            session.add(contact)
            print("✓ Seeded contact information")

            await session.commit()
            print("\n✅ Database seeded successfully!")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Seed failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_seed())
