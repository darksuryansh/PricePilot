import { ExternalLink, Star } from "lucide-react";
import { Button } from "./ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";

interface PlatformData {
  price: number;
  originalPrice?: number;
  rating: number;
  reviews: number;
  link: string;
  availability: boolean;
  productName: string;
}

interface PriceTableProps {
  amazon: PlatformData;
  flipkart: PlatformData;
  myntra: PlatformData;
  meesho?: PlatformData;
}

export function PriceTable({ amazon, flipkart, myntra, meesho }: PriceTableProps) {
  const platforms = [
    { name: 'Amazon', data: amazon, logo: '🟠', color: 'text-orange-600' },
    { name: 'Flipkart', data: flipkart, logo: '🔵', color: 'text-blue-600' },
    { name: 'Myntra', data: myntra, logo: '🩷', color: 'text-pink-600' }
  ];

  // Add Meesho if available
  if (meesho && meesho.availability) {
    platforms.push({ name: 'Meesho', data: meesho, logo: '🟣', color: 'text-purple-600' });
  }

  // Find lowest price from available platforms
  const availablePrices = platforms
    .filter(p => p.data.availability && p.data.price > 0)
    .map(p => p.data.price);
  const lowestPrice = availablePrices.length > 0 ? Math.min(...availablePrices) : 0;
  
  const availablePlatforms = platforms.filter(p => p.data.availability && p.data.price > 0);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl text-gray-900 dark:text-white">Price Comparison Table</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          {availablePlatforms.length > 0 
            ? `Showing prices from ${availablePlatforms.length} platform${availablePlatforms.length > 1 ? 's' : ''}`
            : 'No cross-platform data available yet'}
        </p>
      </div>

      {availablePlatforms.length === 0 ? (
        <div className="p-8 text-center">
          <p className="text-gray-500 dark:text-gray-400 mb-2">
            This product is only available on one platform currently.
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500">
            Scrape the same product from other platforms to see price comparisons.
          </p>
        </div>
      ) : (
        <>
          {/* Desktop Table */}
          <div className="hidden md:block overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Retailer</TableHead>
              <TableHead>Product</TableHead>
              <TableHead>Rating</TableHead>
              <TableHead>Price</TableHead>
              <TableHead>Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {platforms
              .filter(p => p.data.availability && p.data.price > 0) // Only show platforms with actual data
              .map((platform) => (
              <TableRow key={platform.name} className={platform.data.price === lowestPrice && lowestPrice > 0 ? 'bg-green-50' : ''}>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{platform.logo}</span>
                    <span className={platform.color}>{platform.name}</span>
                    {platform.data.price === lowestPrice && lowestPrice > 0 && (
                      <Badge className="bg-green-600 text-white">Lowest</Badge>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  {platform.data.link && platform.data.link !== '#' ? (
                    <a href={platform.data.link} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline line-clamp-2 max-w-xs">
                      {platform.data.productName}
                    </a>
                  ) : (
                    <span className="text-sm text-gray-700 line-clamp-2 max-w-xs">
                      {platform.data.productName}
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  {platform.data.rating > 0 ? (
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span>{platform.data.rating.toFixed(1)}</span>
                      <span className="text-xs text-gray-500">({platform.data.reviews.toLocaleString()})</span>
                    </div>
                  ) : (
                    <span className="text-sm text-gray-500">No ratings</span>
                  )}
                </TableCell>
                <TableCell>
                  <div className="space-y-1">
                    <div className="text-xl font-semibold text-gray-900">₹{platform.data.price.toLocaleString()}</div>
                    {platform.data.originalPrice && platform.data.originalPrice > platform.data.price && (
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500 line-through">
                          ₹{platform.data.originalPrice.toLocaleString()}
                        </span>
                        <Badge variant="secondary" className="bg-green-100 text-green-700 text-xs">
                          {Math.round(((platform.data.originalPrice - platform.data.price) / platform.data.originalPrice) * 100)}% off
                        </Badge>
                      </div>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  {platform.data.link && platform.data.link !== '#' ? (
                    <Button
                      asChild
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      <a href={platform.data.link} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Buy Now
                      </a>
                    </Button>
                  ) : (
                    <Button disabled className="bg-gray-300 cursor-not-allowed">
                      <ExternalLink className="h-4 w-4 mr-2" />
                      No Link
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden divide-y divide-gray-200">
        {platforms.map((platform) => (
          <div key={platform.name} className={`p-4 ${platform.data.price === lowestPrice ? 'bg-green-50' : ''}`}>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{platform.logo}</span>
                  <span className={`${platform.color}`}>{platform.name}</span>
                </div>
                {platform.data.price === lowestPrice && (
                  <Badge className="bg-green-600 text-white">Lowest</Badge>
                )}
              </div>

              <div className="flex items-center gap-1 text-sm">
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                <span>{platform.data.rating.toFixed(1)}</span>
                <span className="text-xs text-gray-500">({platform.data.reviews.toLocaleString()} reviews)</span>
              </div>

              <div className="flex items-baseline justify-between">
                <div className="text-2xl">₹{platform.data.price.toLocaleString()}</div>
                {platform.data.originalPrice && platform.data.originalPrice > platform.data.price && (
                  <Badge variant="secondary" className="bg-green-100 text-green-700">
                    {Math.round(((platform.data.originalPrice - platform.data.price) / platform.data.originalPrice) * 100)}% off
                  </Badge>
                )}
              </div>

              {!platform.data.availability && (
                <Badge variant="destructive">Out of Stock</Badge>
              )}

              <Button
                asChild
                disabled={!platform.data.availability}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                <a href={platform.data.link} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Buy on {platform.name}
                </a>
              </Button>
            </div>
          </div>
        ))}
      </div>
        </>
      )}
    </div>
  );
}
